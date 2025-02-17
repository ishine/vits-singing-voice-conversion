import os
import numpy as np
import librosa
import pyworld


def compute_f0(path):
    x, sr = librosa.load(path, sr=16000)
    assert sr == 16000
    f0, t = pyworld.dio(
        x.astype(np.double),
        fs=sr,
        f0_ceil=900,
        frame_period=1000 * 160 / sr,
    )
    f0 = pyworld.stonemask(x.astype(np.double), f0, t, fs=16000)
    for index, pitch in enumerate(f0):
        f0[index] = round(pitch, 1)
    return f0


if __name__ == "__main__":
    os.makedirs("filelists", exist_ok=True)
    files = open("./filelists/train.txt", "w", encoding="utf-8")

    rootPath = "./data_svc/waves-16k/"
    outPath = "./data_svc/pitch/"
    os.makedirs(outPath, exist_ok=True)

    for file in os.listdir(f"./{rootPath}"):
        if file.endswith(".wav"):
            file = file[:-4]
            wav_path = f"./{rootPath}//{file}.wav"
            featur_pit = compute_f0(wav_path)

            np.save(
                f"{outPath}//{file}.pit",
                featur_pit,
                allow_pickle=False,
            )

            path_spk = "./data_svc/lora_speaker.npy"
            path_wave = f"./data_svc/waves-48k/{file}.wav"
            path_pitch = f"./data_svc/pitch/{file}.pit.npy"
            path_whisper = f"./data_svc/whisper/{file}.ppg.npy"
            print(
                f"{path_wave}|{path_pitch}|{path_whisper}|{path_spk}",
                file=files,
            )

    files.close()
