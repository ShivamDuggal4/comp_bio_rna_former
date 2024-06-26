import torch
import torch.nn as nn
from torch import Tensor
from typing import Any, Callable, List, Optional, Type, Union

from RNAformer.module.embedding import EmbedSequence2Matrix
from RNAformer.model.RNAformer_stack import RNAformerStack


def conv3x3(in_planes: int, out_planes: int, stride: int = 1, groups: int = 1, dilation: int = 1) -> nn.Conv2d:
    """3x3 convolution with padding"""
    return nn.Conv2d(
        in_planes,
        out_planes,
        kernel_size=3,
        stride=stride,
        padding=dilation,
        groups=groups,
        bias=False,
        dilation=dilation,
    )


def conv1x1(in_planes: int, out_planes: int, stride: int = 1) -> nn.Conv2d:
    """1x1 convolution"""
    return nn.Conv2d(in_planes, out_planes, kernel_size=1, stride=stride, bias=False)


class BasicBlock(nn.Module):
    expansion: int = 1

    def __init__(
        self,
        inplanes: int,
        planes: int,
        stride: int = 1,
        downsample: Optional[nn.Module] = None,
        groups: int = 1,
        base_width: int = 64,
        dilation: int = 1,
        norm_layer: Optional[Callable[..., nn.Module]] = None,
    ) -> None:
        super().__init__()
        if norm_layer is None:
            norm_layer = nn.BatchNorm2d
        if groups != 1 or base_width != 64:
            raise ValueError("BasicBlock only supports groups=1 and base_width=64")
        if dilation > 1:
            raise NotImplementedError("Dilation > 1 not supported in BasicBlock")
        # Both self.conv1 and self.downsample layers downsample the input when stride != 1
        self.conv1 = conv3x3(inplanes, planes, stride)
        self.bn1 = norm_layer(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = conv3x3(planes, planes)
        self.bn2 = norm_layer(planes)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x: Tensor) -> Tensor:
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            identity = self.downsample(x)

        out += identity
        out = self.relu(out)

        return out



class ResNet(nn.Module):
    def __init__(
        self,
        block: Type[Union[BasicBlock]],
        layers: List[int],
        num_classes: int = 1000,
        zero_init_residual: bool = False,
        groups: int = 1,
        width_per_group: int = 64,
        replace_stride_with_dilation: Optional[List[bool]] = None,
        norm_layer: Optional[Callable[..., nn.Module]] = None,
    ) -> None:
        super().__init__()
        if norm_layer is None:
            norm_layer = nn.BatchNorm2d
        self._norm_layer = norm_layer

        self.inplanes = 256
        self.dilation = 1
        if replace_stride_with_dilation is None:
            # each element in the tuple indicates if we should replace
            # the 2x2 stride with a dilated convolution instead
            replace_stride_with_dilation = [True, True, True]
        if len(replace_stride_with_dilation) != 3:
            raise ValueError(
                "replace_stride_with_dilation should be None "
                f"or a 3-element tuple, got {replace_stride_with_dilation}"
            )
        self.groups = groups
        self.base_width = width_per_group
        # self.conv1 = nn.Conv2d(3, self.inplanes, kernel_size=7, stride=2, padding=3, bias=False)
        # self.bn1 = norm_layer(self.inplanes)
        # self.relu = nn.ReLU(inplace=True)
        # self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(block, 256, layers[0])
        self.layer2 = self._make_layer(block, 256, layers[1], stride=1, dilate=replace_stride_with_dilation[0])
        self.layer3 = self._make_layer(block, 256, layers[2], stride=1, dilate=replace_stride_with_dilation[1])
        self.layer4 = self._make_layer(block, 256, layers[3], stride=1, dilate=replace_stride_with_dilation[2])
        # self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        # self.fc = nn.Linear(512 * block.expansion, num_classes)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode="fan_out", nonlinearity="relu")
            elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

        # Zero-initialize the last BN in each residual branch,
        # so that the residual branch starts with zeros, and each residual block behaves like an identity.
        # This improves the model by 0.2~0.3% according to https://arxiv.org/abs/1706.02677
        if zero_init_residual:
            for m in self.modules():
                if isinstance(m, BasicBlock) and m.bn2.weight is not None:
                    nn.init.constant_(m.bn2.weight, 0)  # type: ignore[arg-type]

    def _make_layer(
        self,
        block: Type[Union[BasicBlock]],
        planes: int,
        blocks: int,
        stride: int = 1,
        dilate: bool = False,
    ) -> nn.Sequential:
        norm_layer = self._norm_layer
        downsample = None
        previous_dilation = self.dilation
        if dilate:
            self.dilation *= stride
            stride = 1
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                conv1x1(self.inplanes, planes * block.expansion, stride),
                norm_layer(planes * block.expansion),
            )

        layers = []
        layers.append(
            block(
                self.inplanes, planes, stride, downsample, self.groups, self.base_width, previous_dilation, norm_layer
            )
        )
        self.inplanes = planes * block.expansion
        for _ in range(1, blocks):
            layers.append(
                block(
                    self.inplanes,
                    planes,
                    groups=self.groups,
                    base_width=self.base_width,
                    dilation=self.dilation,
                    norm_layer=norm_layer,
                )
            )

        return nn.Sequential(*layers)
    

    def _forward_impl(self, x: Tensor) -> Tensor:
        # See note [TorchScript super()]
        # x = self.conv1(x)
        # x = self.bn1(x)
        # x = self.relu(x)
        # x = self.maxpool(x)
        
        x = x.permute([0,3,1,2])
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = x.permute([0,2,3, 1])
        
        # x = self.avgpool(x)
        # x = torch.flatten(x, 1)
        # x = self.fc(x)
        return x

    def forward(self, x: Tensor) -> Tensor:
        return self._forward_impl(x)

class RiboFormer(nn.Module):

    def __init__(self, config):
        super().__init__()

        self.model_dim = config.model_dim

        if hasattr(config, "cycling") and config.cycling:
            self.initialize_cycling(config.cycling)
        else:
            self.cycling = False

        self.seq2mat_embed = EmbedSequence2Matrix(config)
        # self.RNAformer = RNAformerStack(config)

        if not hasattr(config, "pdb_flag") or config.pdb_flag:
            self.pdf_embedding = nn.Linear(1, config.model_dim, bias=True)
            self.use_pdb = True
        else:
            self.use_pdb = False

        if not hasattr(config, "binary_output") or config.binary_output:
            self.output_mat = nn.Linear(config.model_dim, 1, bias=True)
        else:
            self.output_mat = nn.Linear(config.model_dim, 2, bias=False)

        # self.sigmoid = nn.Sigmoid()
        # self.log_softmax = nn.LogSoftmax(dim=-1)

        self.resnet = ResNet(BasicBlock, layers=[2,2,2,2])
        self.initialize(initializer_range=config.initializer_range)

    def initialize(self, initializer_range):

        nn.init.normal_(self.output_mat.weight, mean=0.0, std=initializer_range)

    def initialize_cycling(self, cycle_steps):
        import random
        self.cycling = True
        self.cycle_steps = cycle_steps
        self.recycle_pair_norm = nn.LayerNorm(self.model_dim, elementwise_affine=True)
        self.trng = torch.Generator()
        self.trng.manual_seed(random.randint(1, 10000))

    def make_pair_mask(self, src, src_len):
        encode_mask = torch.arange(src.shape[1], device=src.device).expand(src.shape[:2]) < src_len.unsqueeze(1)

        pair_mask = encode_mask[:, None, :] * encode_mask[:, :, None]

        assert isinstance(pair_mask, torch.BoolTensor) or isinstance(pair_mask, torch.cuda.BoolTensor)
        return torch.bitwise_not(pair_mask)

    # @torch.no_grad()
    # def cycle_riboformer(self, pair_act, pair_mask):
    #     latent = self.RNAformer(pair_act=pair_act, pair_mask=pair_mask, cycle_infer=True)
    #     return latent.detach()

    @torch.no_grad()
    def cycle_resnet(self, latent):
        latent = self.resnet(latent)
        return latent.detach()

    def forward(self, src_seq, src_len, pdb_sample, max_cycle=0):

        pair_mask = self.make_pair_mask(src_seq, src_len)
        pair_latent, _ = self.seq2mat_embed(src_seq)
        
        if self.use_pdb:
            pair_latent = pair_latent + self.pdf_embedding(pdb_sample)[:, None, None, :]
            
        # latent = pair_latent
        # latent = self.resnet(pair_latent) # uncomment this and comment everything below till output_mat for resnt with cycles.

        if self.cycling:
            if self.training:
                n_cycles = torch.randint(0, max_cycle + 1, [1])
                n_cycles = n_cycles.item()
            else:
                n_cycles = self.cycle_steps

            print('running cycles: ', n_cycles)
            cyc_latent = torch.zeros_like(pair_latent)
            for n in range(n_cycles - 1):
                res_latent = pair_latent.detach() + self.recycle_pair_norm(cyc_latent.detach()).detach()
                print(n, ' th cycle run with layernorm.')
                cyc_latent = self.cycle_resnet(res_latent) 

        pair_latent = pair_latent + self.recycle_pair_norm(cyc_latent.detach())
        latent = self.resnet(pair_latent) # + latent.detach()      
        logits = self.output_mat(latent)
        
        return logits, pair_mask

        # latent = pair_latent
        # if self.cycling:
        #     if self.training:
        #         n_cycles = torch.randint(0, max_cycle + 1, [1])
        #         n_cycles = n_cycles.item()
        #     else:
        #         n_cycles = self.cycle_steps

        #     print('running cycles: ', n_cycles)
        #     for n in range(n_cycles - 1):
        #         print(n, ' th cycle run.')
        #         latent = self.cycle_resnet(latent.detach()) + latent.detach()