# singing voice conversion based on whisper & maxgan
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/17PK5Vd-oyoxpsZ8nENktFcPZEwZmPrTb?usp=sharing)
<img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/PlayVoice/lora-svc">
<img alt="GitHub forks" src="https://img.shields.io/github/forks/PlayVoice/lora-svc">
<img alt="GitHub issues" src="https://img.shields.io/github/issues/PlayVoice/lora-svc">
<img alt="GitHub" src="https://img.shields.io/github/license/PlayVoice/lora-svc">

[【中文说明】](README_zh_CN.md)

```
基于人工智能三大巨头的黑科技：

来至OpenAI的whisper，68万小时多种语言

来至Nvidia的bigvgan，语音生成抗锯齿

来至Microsoft的adapter，高效率微调
```
插件式开源歌声声库模型，依据LoRA原理：

<p align="center">
  <img src="https://user-images.githubusercontent.com/16432329/225337790-392b958a-67ec-4643-b26a-018ee8e4cf56.jpg" />
</p>

基于大量数据，从零开始训练模型，使用分支：[lora-svc-for-pretrain](https://github.com/PlayVoice/lora-svc/tree/lora-svc-for-pretrain)

https://user-images.githubusercontent.com/16432329/231021007-6e34cbb4-e256-491d-8ab6-5ce4e822da21.mp4

下面是基于预训练模型定制专有音色

## 训练

- 1 数据准备，将原始音频数据放到 `./data_svc/waves-raw` 目录下

    转换采样率为`16000Hz`
    
    > python svc_preprocess_wav.py --out_dir ./data_svc/waves-16k --sr 16000

    转换采样率为`48000Hz`, 将音频数据放到 `./data_svc/waves-48k`

    > python svc_preprocess_wav.py --out_dir ./data_svc/waves-48k --sr 48000

- 2 下载音色编码器: [Speaker-Encoder by @mueller91](https://drive.google.com/drive/folders/15oeBYf6Qn1edONkVLXe82MzdIi3O_9m3), 解压文件，把 `best_model.pth.tar`  放到目录 `speaker_pretrain/`

    提取每个音频文件的音色
    
    > python svc_preprocess_speaker.py ./data_svc/waves-16k ./data_svc/speaker

- 3 下载whisper模型 [multiple language medium model](https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt), 确定下载的是`medium.pt`，把它放到文件夹 `whisper_pretrain/` 中，提取每个音频的内容编码

    > sudo apt update && sudo apt install ffmpeg

    > python svc_preprocess_ppg.py -w ./data_svc/waves-16k -p ./data_svc/whisper

- 4 提取基音，同时生成训练文件 `filelist/train.txt`，剪切train的前5条用于制作`filelist/eval.txt`

    > python svc_preprocess_f0.py

- 5 取所有音频音色的平均作为目标发音人的音色，并完成声域分析
    
    > python svc_preprocess_speaker_lora.py ./data_svc/

    生成 lora_speaker.npy 和 lora_pitch_statics.npy 两个文件

- 6 从release页面下载预训练模型`maxgan_pretrain_48K_5L.pth`，放到model_pretrain文件夹中，预训练模型中包含了生成器和判别器

    https://github.com/PlayVoice/lora-svc/blob/622fafca87d877a89717aeb09337afbadd885941/config/maxgan.yaml#L17

    > python svc_trainer.py -c config/maxgan.yaml -n lora
    
    恢复训练
    
    > python svc_trainer.py -c config/maxgan.yaml -n lora -p chkpt/lora/***.pth


你的文件目录应该长这个样子~~~

    data_svc/
    │
    └── lora_speaker.npy
    │
    └── lora_pitch_statics.npy
    │
    └── pitch
    │     ├── 000001.pit.npy
    │     ├── 000002.pit.npy
    │     └── 000003.pit.npy
    └── speakers
    │     ├── 000001.spk.npy
    │     ├── 000002.spk.npy
    │     └── 000003.spk.npy
    └── waves-16k
    │     ├── 000001.wav
    │     ├── 000002.wav
    │     └── 000003.wav
    └── waves-48k
    │     ├── 000001.wav
    │     ├── 000002.wav
    │     └── 000003.wav
    └── whisper
          ├── 000001.ppg.npy
          ├── 000002.ppg.npy
          └── 000003.ppg.npy
## 训练LoRA

设置开关

https://github.com/PlayVoice/lora-svc/blob/d3a1df57e6019c12513bb34e1bd5c8162d5e5055/config/maxgan.yaml#L16


https://github.com/PlayVoice/lora-svc/blob/d3a1df57e6019c12513bb34e1bd5c8162d5e5055/utils/train.py#L34-L35

使用场景

- 极低资源，防止过拟合

- 插件式声库开发

- 其他场景，建议关闭

## egs: 使用50句猫雷、训练十分钟的日志如下
https://user-images.githubusercontent.com/16432329/228889388-d7658930-6187-48a8-af37-74096d41c018.mp4

## 推理
- 1 导出生成器，判别器只会在训练中用到

    > python svc_inference_export.py --config config/maxgan.yaml --checkpoint_path chkpt/lora/lora_0090.pt

    导出的模型在当前文件夹maxgan_g.pth，文件大小为`54.3M`；maxgan_lora.pth为微调模块，文件大小为`0.94M`。

- 2 使用whisper提取内容编码，没有采用一键推理，为了降低显存占用

    > python svc_inference_ppg.py -w test.wav -p test.ppg.npy

    生成test.ppg.npy；如果下一步没有指定ppg文件，则调用程序自动生成

- 3 指定参数，推理

    > python svc_inference.py --config config/maxgan.yaml --model maxgan_g.pth --spk ./data_svc/`lora_speaker.npy` --wave test.wav --ppg test.ppg.npy

    生成文件在当前目录svc_out.wav；同时生成svc_out_pitch.wav，用于直观显示基音提取结果。

**啥**？生成的音色不太像！

- 1 发音人音域统计

    训练第5步生成：lora_pitch_statics.npy

- 2 推理音区偏移

    指定pitch参数：
    
    > python svc_inference.py --config config/maxgan.yaml --model maxgan_g.pth --spk ./data_svc/lora_speaker.npy --statics ./data_svc/lora_pitch_statics.npy --wave test.wav


## 频率扩展：16K->48K `48K版本用不上`

> python svc_bandex.py -w svc_out.wav

在当前目录生成svc_out_48k.wav

## 音质增强

从 [DiffSinger 社区声码器项目](https://openvpi.github.io/vocoders) 下载基于预训练声码器的增强器，并解压至 `nsf_hifigan_pretrain/` 文件夹。
注意：你应当下载名称中带有`nsf_hifigan`的压缩文件，而非`nsf_hifigan_finetune`。

将频率扩张后生成的svc_out_48k.wav复制到path\to\input\wavs，运行

>python svc_val_nsf_hifigan.py

在path\to\output\wavs生成增强后的文件

## 代码来源和参考文献
[Adapter-Based Extension of Multi-Speaker Text-to-Speech Model for New Speakers](https://arxiv.org/abs/2211.00585)

[AdaSpeech: Adaptive Text to Speech for Custom Voice](https://arxiv.org/pdf/2103.00993.pdf)

https://github.com/nii-yamagishilab/project-NN-Pytorch-scripts/tree/master/project/01-nsf

https://github.com/mindslab-ai/univnet [[paper]](https://arxiv.org/abs/2106.07889)

https://github.com/openai/whisper/ [[paper]](https://arxiv.org/abs/2212.04356)

https://github.com/NVIDIA/BigVGAN [[paper]](https://arxiv.org/abs/2206.04658)

https://github.com/brentspell/hifi-gan-bwe

https://github.com/openvpi/DiffSinger

https://github.com/chenwj1989/pafx

## 贡献者

<a href="https://github.com/PlayVoice/lora-svc/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=PlayVoice/lora-svc" />
</a>

## 注意事项
If you adopt the code or idea of this project, please list it in your project, which is the basic criterion for the continuation of the open source spirit.

如果你采用了本项目的代码或创意，请在你的项目中列出，这是开源精神得以延续的基本准则。

このプロジェクトのコードやアイデアを採用した場合は、オープンソースの精神が続く基本的なガイドラインであるプロジェクトにリストしてください。
