"""V1 FlirtGPT architecture and checkpoint-backed response generation."""

from __future__ import annotations

import logging
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F

LOGGER = logging.getLogger("flirtgpt")
CHECKPOINT_PATH = Path(__file__).resolve().parents[1] / "flirtgpt.pt"


class Head(nn.Module):
    def __init__(self, n_embd: int, head_size: int, block_size: int):
        super().__init__()
        self.key = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer("tril", torch.tril(torch.ones(block_size, block_size)))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        _, length, _ = x.shape
        k, q, v = self.key(x), self.query(x), self.value(x)
        weights = q @ k.transpose(-2, -1) * (k.shape[-1] ** -0.5)
        weights = weights.masked_fill(self.tril[:length, :length] == 0, float("-inf"))
        return F.softmax(weights, dim=-1) @ v


class MultiHeadAttention(nn.Module):
    def __init__(self, n_embd: int, n_head: int, block_size: int):
        super().__init__()
        head_size = n_embd // n_head
        self.heads = nn.ModuleList([Head(n_embd, head_size, block_size) for _ in range(n_head)])
        self.proj = nn.Linear(n_embd, n_embd)
        self.dropout = nn.Dropout(0.0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.proj(torch.cat([head(x) for head in self.heads], dim=-1))


class FeedForward(nn.Module):
    def __init__(self, n_embd: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd), nn.ReLU(), nn.Linear(4 * n_embd, n_embd), nn.Dropout()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class Block(nn.Module):
    def __init__(self, n_embd: int, n_head: int, block_size: int):
        super().__init__()
        self.sa = MultiHeadAttention(n_embd, n_head, block_size)
        self.ffwd = FeedForward(n_embd)
        self.ln1 = nn.LayerNorm(n_embd)
        self.ln2 = nn.LayerNorm(n_embd)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.sa(self.ln1(x))
        return x + self.ffwd(self.ln2(x))


class GPTLanguageModel(nn.Module):
    """Architecture matching the GPTLanguageModel saved by flirt_gpt.ipynb V1."""

    def __init__(self, vocab_size: int, n_embd: int, n_head: int, n_layer: int, block_size: int):
        super().__init__()
        self.block_size = block_size
        self.token_embedding_table = nn.Embedding(vocab_size, n_embd)
        self.position_embedding_table = nn.Embedding(block_size, n_embd)
        self.blocks = nn.Sequential(*[Block(n_embd, n_head, block_size) for _ in range(n_layer)])
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)

    def forward(self, idx: torch.Tensor):
        _, length = idx.shape
        positions = torch.arange(length, device=idx.device)
        x = self.token_embedding_table(idx) + self.position_embedding_table(positions)
        return self.lm_head(self.ln_f(self.blocks(x)))

    @torch.no_grad()
    @torch.no_grad()
    def generate(
        self,
        idx: torch.Tensor,
        max_new_tokens: int,
        temperature: float = 0.8,
        top_k: int = 20,
        repetition_penalty: float = 1.1,
    ):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.block_size:]

            logits = self(idx_cond)[:, -1, :]
            logits = logits / temperature

            # Penalize characters that have appeared recently.
            recent_tokens = idx_cond[:, -32:]

            for token in torch.unique(recent_tokens):
                token_id = token.item()

                if logits[0, token_id] < 0:
                    logits[0, token_id] *= repetition_penalty
                else:
                    logits[0, token_id] /= repetition_penalty

            if top_k is not None:
                values, _ = torch.topk(
                    logits,
                    min(top_k, logits.size(-1))
                )
                logits[logits < values[:, [-1]]] = float("-inf")

            probs = F.softmax(logits, dim=-1)

            next_token = torch.multinomial(
                probs,
                num_samples=1
            )

            idx = torch.cat((idx, next_token), dim=1)

        return idx


class FlirtGPT:
    def __init__(self, checkpoint_path: Path = CHECKPOINT_PATH):
        if not checkpoint_path.is_file():
            raise FileNotFoundError("The FlirtGPT V1 checkpoint is missing.")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
        required = {"model_state_dict", "vocab_size", "n_embd", "n_head", "n_layer", "block_size", "chars"}
        if not required.issubset(checkpoint):
            raise ValueError("The checkpoint does not contain the expected FlirtGPT V1 configuration.")
        self.chars = checkpoint["chars"]
        self.stoi = {char: index for index, char in enumerate(self.chars)}
        self.itos = {index: char for index, char in enumerate(self.chars)}
        self.block_size = int(checkpoint["block_size"])
        self.model = GPTLanguageModel(
            vocab_size=int(checkpoint["vocab_size"]), n_embd=int(checkpoint["n_embd"]),
            n_head=int(checkpoint["n_head"]), n_layer=int(checkpoint["n_layer"]), block_size=self.block_size,
        ).to(self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()
        LOGGER.info("FlirtGPT loaded on %s", self.device)

    def respond(self, messages: list[dict[str, str]]) -> str:
        latest = messages[-1]

        prompt = (
            f"<|user|>\n"
            f"{latest['content'].strip()}\n"
            f"<|assistant|>\n"
        )

        encoded = [
            self.stoi[char]
            for char in prompt
            if char in self.stoi
        ]

        if not encoded:
            raise ValueError(
                "Message contains no characters supported by this model."
            )

        input_tensor = torch.tensor(
            [encoded[-self.block_size:]],
            dtype=torch.long,
            device=self.device,
        )

        with torch.no_grad():
            generated = self.model.generate(
                input_tensor,
                max_new_tokens=80,
                temperature=0.75,
                top_k=20,
                repetition_penalty=1.1,
            )

        decoded = "".join(
            self.itos[int(token)]
            for token in generated[0].tolist()
        )

        response = decoded.rsplit(
            "<|assistant|>\n",
            1
        )[-1]

        response = response.split(
            "<|user|>",
            1
        )[0]

        response = response.split(
            "<|assistant|>",
            1
        )[0]

        return response.strip()

    @staticmethod
    def _prompt(messages: list[dict[str, str]]) -> str:
        return "".join(f"<|{item['role']}|>\n{item['content'].strip()}\n" for item in messages) + "<|assistant|>\n"
