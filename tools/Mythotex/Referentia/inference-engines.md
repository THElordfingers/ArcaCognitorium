# Inference Engines
*Mythotex — forge speed reference*

---

## What is an Inference Engine?

When Mythotex generates an image, it has to run a neural network hundreds
of times per generation — each pass refining a field of noise into a
coherent picture. The **inference engine** is what actually executes those
passes: the software stack, model format, and hardware pathway used to do
the maths.

Choosing the right engine is the single biggest lever you have on speed.
The three engines available in Mythotex are not just settings — they are
fundamentally different approaches to the same problem.

---

## The Three Engines

### 1 — Standard SD 1.5

```
╔══════════════════════╦══════════════════════════════════════════════════╗
║ Model                ║ runwayml/stable-diffusion-v1-5                  ║
║ Backend              ║ PyTorch / diffusers                              ║
║ Recommended steps    ║ 20–40                                            ║
║ Recommended CFG      ║ 7–9                                              ║
║ Negative prompts     ║ Supported                                        ║
║ Speed (Raphael CPU)  ║ Slowest — baseline                               ║
╚══════════════════════╩══════════════════════════════════════════════════╝
```

The original Stable Diffusion 1.5 model, running through Hugging Face
diffusers in Python. This is the reference implementation — well understood,
extensively documented, and compatible with the widest range of LoRAs,
samplers, and techniques.

**How it works.** Each generation step runs the UNet (a large convolutional
neural network) once in float32 or float16 arithmetic. With 25 steps, that's
25 full UNet forward passes. On a CPU without GPU acceleration, each pass
takes several seconds — which is why generation can take ten minutes or more
on modest hardware.

**Samplers.** Standard mode exposes four samplers, each a different
mathematical method for walking from noise to image:

```
╔══════════════╦═══════════════════════════════════════════════════════════╗
║ Sampler      ║ Character                                                 ║
╠══════════════╬═══════════════════════════════════════════════════════════╣
║ Euler        ║ Simple, fast convergence. Good default.                   ║
╠══════════════╬═══════════════════════════════════════════════════════════╣
║ DPM++ 2M     ║ Multi-step solver. Better detail at same step count.      ║
╠══════════════╬═══════════════════════════════════════════════════════════╣
║ LMS          ║ Linear multi-step. Smooth gradients, slightly softer.     ║
╠══════════════╬═══════════════════════════════════════════════════════════╣
║ PNDM         ║ Pseudo-numerical. Fast but occasionally unstable at       ║
║              ║ low step counts.                                          ║
╚══════════════╩═══════════════════════════════════════════════════════════╝
```

**When to use it.** When you need maximum control — specific samplers,
higher CFG values, aggressive negative prompts — or when you're
troubleshooting image quality and want the known reference behaviour. Pair
with INT8 quantisation and torch.compile to recover some speed.

---

### 2 — LCM  *(default)*

```
╔══════════════════════╦══════════════════════════════════════════════════╗
║ Model                ║ SimianLuo/LCM_Dreamshaper_v7                    ║
║ Backend              ║ PyTorch / diffusers + LCMScheduler               ║
║ Recommended steps    ║ 4–8                                              ║
║ Recommended CFG      ║ 1–2                                              ║
║ Negative prompts     ║ Not supported (cleared automatically)            ║
║ Speed (Raphael CPU)  ║ ~4–6× faster than Standard                      ║
╚══════════════════════╩══════════════════════════════════════════════════╝
```

**Latent Consistency Models** are a fundamentally different approach to
diffusion inference. Standard diffusion has to take many small steps because
each step only moves a little way through the noise. LCM is trained to
predict the final image directly from any intermediate noise level — a
technique called *consistency distillation* — which means it can reach a
coherent result in as few as 4 steps.

The underlying architecture is identical to SD 1.5. The weights are
different; the scheduler is different; everything else in the pipeline
remains the same. This is why it slots in as a drop-in replacement with no
extra dependencies.

**LCM Dreamshaper v7** is the specific checkpoint used here — a
fantasy-art fine-tuned model that has been further distilled for LCM
inference. Its aesthetic register matches Mythotex's output goals
particularly well.

**CFG in LCM.** Classifier-Free Guidance (the CFG scale) controls how
strongly the model follows the prompt versus exploring freely. In standard
diffusion, values of 7–12 are typical. In LCM, the distillation process
bakes guidance into the weights — raising CFG past 2 causes the model to
overcorrect and produces degraded, oversaturated, or artefacted output.
Keep it at 1–2.

**Negative prompts.** The LCM scheduler does not implement the negative
prompt pathway. Any text in the negative prompt field is silently ignored.
Mythotex clears the negative prompt automatically when LCM is selected.
This is not a limitation you can work around with clever prompting — it is
a structural property of how LCM inference works.

**When to use it.** Always, unless you have a specific reason not to. LCM
is the default engine because on CPU-constrained hardware it is the only
way to get results in a reasonable timeframe. The quality difference versus
Standard at equivalent step counts is minimal for object illustration.

---

### 3 — sd.cpp  *(requires manual build)*

```
╔══════════════════════╦══════════════════════════════════════════════════╗
║ Model                ║ GGUF-quantised .safetensors (user-supplied)      ║
║ Backend              ║ stable-diffusion.cpp — pure C++ subprocess       ║
║ Recommended steps    ║ 15–25                                            ║
║ Recommended CFG      ║ 6–8                                              ║
║ Negative prompts     ║ Supported                                        ║
║ Speed (Raphael CPU)  ║ Fastest — best raw CPU throughput                ║
╚══════════════════════╩══════════════════════════════════════════════════╝
```

`stable-diffusion.cpp` is a C++ reimplementation of Stable Diffusion that
runs entirely outside of Python. Where diffusers runs models through
PyTorch's abstractions — designed for flexibility and GPU work — sd.cpp
compiles directly against your CPU's instruction set, using AVX2 and
AVX512 SIMD intrinsics to execute matrix operations in parallel across your
cores with minimal overhead.

**Why C++ is faster on CPU.** PyTorch carries significant overhead per
operation: Python interpreter, tensor bookkeeping, dispatch logic,
gradient tracking infrastructure. On a GPU this overhead is invisible
because a single GPU operation might take milliseconds. On CPU, where
individual operations take much longer relative to overhead, that cost
adds up. sd.cpp bypasses all of it — the model runs as tightly compiled
native code.

**GGUF quantisation.** sd.cpp loads models in GGUF format with integer
quantisation (typically Q4_K_M or Q8_0). A Q4 model stores each weight
as a 4-bit integer rather than a 32-bit float, reducing model size by ~8×
and allowing more of it to sit in CPU cache where access is fast. The
quality loss at Q4 is generally imperceptible for illustration work.

**Subprocess architecture.** Mythotex calls sd.cpp as an external process,
passing prompt, seed, steps, and output path as command-line arguments.
Progress output is streamed from the process and displayed in the progress
bar in real time. This means sd.cpp runs completely independently of the
Python process — it won't interfere with the Qt UI thread and doesn't share
memory with diffusers.

**Build requirement.** sd.cpp must be compiled from source. Pre-built
binaries are not distributed. The build takes 2–5 minutes and requires
`cmake` and a C++17 compiler:

```bash
git clone https://github.com/leejet/stable-diffusion.cpp
cd stable-diffusion.cpp
git submodule init && git submodule update --recursive
mkdir build && cd build
cmake .. -DGGML_AVX2=ON
cmake --build . --config Release -j$(nproc)
```

Place the binary at `~/sd.cpp/build/bin/sd` and a model at
`~/Mythotex/models/v1-5-pruned-emaonly.safetensors`. The binary path and
model path are hardcoded in `Mythotex.py` — edit `SDCPP_BINARY` and the
model path in `_generate_sdcpp()` if your paths differ.

**When to use it.** When you want the fastest possible generation and are
willing to do the build work up front. sd.cpp is particularly effective on
the Raphael because the Ryzen 7000-series CPU has AVX2 and benefits
significantly from the reduced Python overhead. Expected speedup over
Standard SD 1.5 is 2–4× depending on quantisation level and thread count.

---

## Acceleration Layers

The engine choice determines the fundamental execution path. On top of that,
Mythotex provides three acceleration layers that can be combined with any
engine:

### INT8 Quantisation  (`optimum-quanto`)

Converts UNet and text encoder weights from float32 to INT8 at load time.
Halves the memory footprint of the two largest model components and reduces
arithmetic cost by roughly 20% on CPU. Compatible with Standard and LCM
engines. Does not apply to sd.cpp (which handles quantisation internally).

```bash
pip install optimum-quanto
```

Quantisation happens once at engine load — there is no per-generation cost.

### torch.compile

Passes the UNet through PyTorch's compiler with `mode="reduce-overhead"`,
which fuses multiple operations into optimised kernels and eliminates
Python-level dispatch overhead between them. The first generation after
enabling compile is slow (the compiler runs during that pass), but
subsequent generations are faster. The compiled kernel is not persisted
between sessions — the warm-up cost recurs each launch.

Compatible with Standard and LCM. Does not apply to sd.cpp.

### 2× LANCZOS Upscale

Not a speed optimisation — a quality one. After generation at 512×512,
the image is upscaled to 1024×1024 using Lanczos resampling before
background removal. This gives `rembg` a larger input to work with,
producing sharper edges on the transparency mask. The upscale itself is
fast (CPU image processing, not neural inference).

---

## Choosing an Engine

```
╔══════════════════════════════════════════════════╦══════════════════════╗
║ Situation                                        ║ Engine               ║
╠══════════════════════════════════════════════════╬══════════════════════╣
║ Normal use / just want results                   ║ LCM                  ║
╠══════════════════════════════════════════════════╬══════════════════════╣
║ Need negative prompts or specific samplers       ║ Standard SD 1.5      ║
╠══════════════════════════════════════════════════╬══════════════════════╣
║ Want maximum speed, willing to build sd.cpp      ║ sd.cpp               ║
╠══════════════════════════════════════════════════╬══════════════════════╣
║ Long session, can absorb first-run warm-up       ║ LCM + torch.compile  ║
╠══════════════════════════════════════════════════╬══════════════════════╣
║ Memory constrained / slow first loads            ║ Any + INT8 quant     ║
╠══════════════════════════════════════════════════╬══════════════════════╣
║ Diagnosing image quality issues                  ║ Standard SD 1.5      ║
╚══════════════════════════════════════════════════╩══════════════════════╝
```

---

## Approximate Speed on Raphael iGPU (CPU inference)

Times are rough estimates at 512×512. Actual times vary with system load,
RAM speed, and whether models are warm in cache.

```
╔══════════════════════════╦════════╦══════════════════════════════════════╗
║ Configuration            ║ Steps  ║ Estimated time                       ║
╠══════════════════════════╬════════╬══════════════════════════════════════╣
║ Standard SD 1.5          ║ 28     ║ ~8–12 min                            ║
╠══════════════════════════╬════════╬══════════════════════════════════════╣
║ Standard + INT8 + compile║ 28     ║ ~5–8 min                             ║
╠══════════════════════════╬════════╬══════════════════════════════════════╣
║ LCM                      ║ 6      ║ ~2–4 min                             ║
╠══════════════════════════╬════════╬══════════════════════════════════════╣
║ LCM + INT8               ║ 6      ║ ~90 sec – 2.5 min                    ║
╠══════════════════════════╬════════╬══════════════════════════════════════╣
║ LCM + INT8 + compile     ║ 6      ║ ~60–90 sec (after warm-up)           ║
╠══════════════════════════╬════════╬══════════════════════════════════════╣
║ sd.cpp (Q4_K_M)          ║ 20     ║ ~2–4 min                             ║
╠══════════════════════════╬════════╬══════════════════════════════════════╣
║ sd.cpp (Q8_0)            ║ 20     ║ ~3–5 min                             ║
╚══════════════════════════╩════════╩══════════════════════════════════════╝
```

The rembg background removal step adds roughly 10–30 seconds on top of
inference time, regardless of engine.

---

## Switching Engines at Runtime

1. Open **⚙ RITUAL PARAMETERS** in the sidebar
2. Go to the **⚡ ENGINE** tab
3. Select the engine from the dropdown — step and CFG sliders
   auto-adjust to sensible defaults for the selected engine
4. Toggle acceleration options as needed
5. Click **⚡ RELOAD ENGINE** in the sidebar

The pipeline is rebuilt in-place. You do not need to restart Mythotex.
The window title updates to show the active engine name.

---

*Part of the Mythotex / Arca Cognitarium documentation.*
