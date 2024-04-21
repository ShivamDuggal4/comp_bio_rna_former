
CUDA_VISIBLE_DEVICES=2 python3 train_RNAformer.py --config=default_config.yaml experiment.session_name=rna_folding_1 \
experiment.experiment_name=ts0_conform_dim64_32bit \
rna_data.dataframe_path=./datasets/bprna_data.plk \
trainer.precision=32 \
RNAformer.precision=32 \
trainer.devices=1 \
rna_data.batch_size=2 \
rna_data.batch_by_token_size=6 \
RNAformer.binary_output=True
