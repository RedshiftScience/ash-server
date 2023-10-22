# ash configs

bot_name_cfg = "Ashera"
max_tokens_cfg = 2048
tts_backend_cfg = "piper"
llm_backend_cfg = "llamacpp"
grpc_opt_max_send_message_length_cfg = 100 * 1024 * 1024
grpc_opt_max_receive_message_length_cfg = 100 * 1024 * 1024
max_tts_char_cfg = 500

# ip configs

llm_ip_cfg = "127.0.0.1"
llm_port_cfg = 43544
ttts_ip_cfg = "127.0.0.1"
ttts_port_cfg = 43472
piper_ip_cfg = "127.0.0.1"
piper_port_cfg = 50051
rvc_ip_cfg = "127.0.0.1"

rvc_port_cfg = 50052

# llm configs

llama_cpp_temp_cfg = 0.8
llama_cpp_top_k_cfg = 40
llama_cpp_top_p_cfg = 0.9
llama_cpp_n_predict_cfg = 400
llama_cpp_stream_cfg = True
llama_cpp_stop_cfg = "CHAT: \nSYSTEM: \nUser: \n"
llama_cpp_repetition_penalty_cfg = 1.19
llama_cpp_mirostat_mode_cfg = 2
llama_cpp_mirostat_tau_cfg = 2
llama_cpp_mirostat_eta_cfg = 0.2

# tts configs

piper_model_cfg = "ashera.ckpt"
piper_noise_scale_cfg = 0.667
piper_length_scale_cfg = 1.4
piper_noise_scale_w_cfg = 0.8
piper_speaker_id_cfg = 0

# rvc configs

rvc_ssid_cfg = 0
rvc_f0_up_key_cfg = 5.0
rvc_f0_file_cfg = None
rvc_f0_method_cfg = "crepe-tiny"
rvc_file_index_cfg = None
rvc_file_index2_cfg = "logs/ashera2/added_IVF1092_Flat_nprobe_1_ashera2_v2.index"
rvc_index_rate_cfg = 0.0
rvc_filter_radius_cfg = 3
rvc_resample_sr_cfg = 0
rvc_rms_mix_rate_cfg = 1
rvc_protect_cfg = 0.33
rvc_version_cfg = "v2"
rvc_tgt_sr_cfg = 40000

# subtitles configs

subtitles_window_width_cfg = 1920
subtitles_window_height_cfg = 1080
subtitles_title_cfg = "Progressive Words"
subtitles_root_bg_cfg = "red"
subtitles_label_bg_cfg = "red"
subtitles_label_fg_cfg = "white"
subtitles_family_cfg = "Neural BRK"
subtitles_font_size_cfg = 80
subtitles_weight_cfg = "bold"
subtitles_playback_delay_cfg = 0.33
subtitles_start_delay_cfg = 0.7