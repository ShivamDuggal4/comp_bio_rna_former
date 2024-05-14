# python evaluate_RNAformer.py -b -c 2 --state_dict /data/vision/torralba/sduggal/course_work/bio_course_hw/project/RNAProject-self/workspace/experiments_original/RNAformer/rna_folding_1/ts0_conform_dim64_32bit-001/checkpoint-129-19999.0.ckpt/checkpoint/mp_rank_00_model_states.pt  --config models/RNAformer_32M_config_bprna.yml

# python evaluate_RNAformer.py -b -c 6 --state_dict /data/vision/torralba/sduggal/course_work/bio_course_hw/project/RNAProject-self/workspace/experiments_cnn/RNAformer/rna_folding_1/ts0_conform_dim64_32bit-000/checkpoint-48-19999.0.ckpt  --config models/RNAformer_32M_config_bprna.yml #

# python evaluate_RNAformer.py -b -c 6 --state_dict /data/vision/torralba/sduggal/course_work/bio_course_hw/project/RNAProject-self/workspace/experiments_cnn_cycles/RNAformer/rna_folding_1/ts0_conform_dim64_32bit-016/checkpoint-34-14386.0.ckpt  --config models/RNAformer_32M_config_bprna.yml #

# python evaluate_RNAformer.py -b -c 6 --state_dict /data/vision/torralba/sduggal/course_work/bio_course_hw/project/RNAProject-self/workspace/experiments_original_no_cycles/RNAformer/rna_folding_1/ts0_conform_dim64_32bit-016/checkpoint-129-19999.0.ckpt/checkpoint/mp_rank_00_model_states.pt  --config models/RNAformer_32M_config_bprna.yml

python evaluate_RNAformer.py -b -c 1 --state_dict /data/vision/torralba/sduggal/course_work/bio_course_hw/project/RNAProject-self/workspace/experiments_cnn_cycles_retry_2/RNAformer/rna_folding_1/ts0_conform_dim64_32bit-001/checkpoint-48-20138.0.ckpt  --config models/RNAformer_32M_config_bprna.yml #