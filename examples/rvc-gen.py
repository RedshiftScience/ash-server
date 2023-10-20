
import ash_cfgs
import grpc
import ASH_grpc_pb2
import ASH_grpc_pb2_grpc
import time
import threading
lock = threading.Lock()
import soundfile as sf

def rvc(bytes):
    grpc_opt_cfg = [
        ('grpc.max_send_message_length', ash_cfgs.grpc_opt_max_send_message_length_cfg),
        ('grpc.max_receive_message_length', ash_cfgs.grpc_opt_max_receive_message_length_cfg)
    ]

    channel = grpc.insecure_channel(f"{ash_cfgs.rvc_ip_cfg}:{ash_cfgs.rvc_port_cfg}", grpc_opt_cfg)
    rvc_stub = ASH_grpc_pb2_grpc.ServerRVCServiceStub(channel)
    rvc_data = {
        "audio_bytes": bytes,
        "f0_up_key": ash_cfgs.rvc_f0_up_key_cfg,
        "f0_file": ash_cfgs.rvc_f0_file_cfg,
        "f0_method": ash_cfgs.rvc_f0_method_cfg,
        "file_index": ash_cfgs.rvc_file_index_cfg,
        "file_index2": ash_cfgs.rvc_file_index2_cfg,
        "filter_radius": ash_cfgs.rvc_filter_radius_cfg,
        "index_rate": ash_cfgs.rvc_index_rate_cfg,
        "protect": ash_cfgs.rvc_protect_cfg, 
        "resample_sr": ash_cfgs.rvc_resample_sr_cfg,
        "rms_mix_rate": ash_cfgs.rvc_rms_mix_rate_cfg,
        "version": ash_cfgs.rvc_version_cfg,
        "tgt_sr": ash_cfgs.rvc_tgt_sr_cfg
    }

    rvc_request = ASH_grpc_pb2.ServerRVCRequest(**rvc_data)
    rvc_response = rvc_stub.ProcessAudio(rvc_request)

  
    rvc_audio_bytes = rvc_response.audio_bytes


    return rvc_audio_bytes


def main():
    while True:
        input_text = input("input wav path: ")
        if input_text == "exit":
            break
        
        in_bytes = sf.read(input_text)[0].tobytes()
        out_bytes = rvc(in_bytes)
        outpath = input("output wav path: ")
        sf.write(outpath, out_bytes, 40000)

if __name__ == "__main__":
    main()