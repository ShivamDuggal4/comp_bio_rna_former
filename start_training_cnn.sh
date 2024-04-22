
# python3 train_RNAformer.py --config=default_config.yaml experiment.session_name=rna_folding_1 \
# experiment.experiment_name=ts0_conform_dim64_32bit \
# rna_data.dataframe_path=./datasets/bprna_data.plk \
# trainer.precision=32 \
# RNAformer.precision=32 \
# trainer.devices=1 \
# rna_data.batch_size=48 \
# rna_data.batch_by_token_size=False \
# RNAformer.binary_output=True \
# rna_data.max_len=100 \
# experiment.experiments_base_dir=./workspace/experiments_cnn \
# RNAformer.cycling=False


CUDA_VISIBLE_DEVICES=1 python3 train_RNAformer.py --config=default_config.yaml experiment.session_name=rna_folding_1 \
experiment.experiment_name=ts0_conform_dim64_32bit \
rna_data.dataframe_path=./datasets/bprna_data.plk \
trainer.precision=32 \
RNAformer.precision=32 \
trainer.devices=1 \
rna_data.batch_size=48 \
rna_data.batch_by_token_size=False \
RNAformer.binary_output=True \
rna_data.max_len=100 \
experiment.experiments_base_dir=./workspace/experiments_cnn_cycles \
RNAformer.cycling=6 \
resume_training=True \
trainer.resume_from_checkpoint=/data/vision/torralba/sduggal/course_work/bio_course_hw/project/RNAProject-self/workspace/experiments_cnn_cycles/RNAformer/rna_folding_1/ts0_conform_dim64_32bit-006/last.ckpt