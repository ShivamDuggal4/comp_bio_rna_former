import torch
import torch.nn as nn
import math

class ShallowEncoder(nn.Module):
    def __init__(self, input_vocab_size, d_model, nhead, num_encoder_layers, dim_feedforward):
        super(ShallowEncoder, self).__init__()
        self.d_model = d_model
        self.embedding = nn.Embedding(input_vocab_size, d_model)
        self.pos_encoder = nn.Parameter(torch.randn(1, 1, d_model))
        encoder_layer = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_encoder_layers)
        # Output dimension is fixed at 256
        self.output_transform = nn.Linear(d_model, 256)

    def forward(self, src):
        src = self.embedding(src) * math.sqrt(self.d_model)
        src += self.pos_encoder[:, :src.size(1), :]
        output = self.transformer_encoder(src)
        output = self.output_transform(output)
        # Dynamic replication of output across seq_len
        seq_len = output.shape[1]
        output = output.unsqueeze(2).expand(-1, -1, seq_len, -1)
        return output

# # Model hyperparameters
# input_vocab_size = 4  # As you have 4 unique inputs (0, 1, 2, 3)
# d_model = 512  # Size of the embedding
# nhead = 8       # Number of attention heads
# num_encoder_layers = 6  # Number of transformer layers
# dim_feedforward = 2048  # Feedforward network size

# # Initialize model
# model = ShallowEncoder(input_vocab_size, d_model, nhead, num_encoder_layers, dim_feedforward)

# # Example input with varying sequence lengths
# bs = 10  # Batch size
# seq_len1 = 20  # Sequence length for first input
# seq_len2 = 15  # Sequence length for second input
# input_tensor1 = torch.randint(0, input_vocab_size, (bs, seq_len1))
# input_tensor2 = torch.randint(0, input_vocab_size, (bs, seq_len2))

# # Forward pass for different sequence lengths
# output1 = model(input_tensor1)
# output2 = model(input_tensor2)
# print(output1.shape)  # Expected output shape: (bs, seq_len1, seq_len1, 256)
# print(output2.shape)  # Expected output shape: (bs, seq_len2, seq_len2, 256)