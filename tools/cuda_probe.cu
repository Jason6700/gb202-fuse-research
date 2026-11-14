// Read-only CUDA Runtime API device-property probe; no GPU register or fuse writes.
// Compile: nvcc -O2 -o cuda_probe.exe tools/cuda_probe.cu
#include <cuda_runtime.h>
#include <cstdio>
#include <cstdlib>

int main(int argc, char** argv) {
    int index = 0;
    if (argc > 1) index = std::atoi(argv[1]);
    if (index < 0) {
        std::fprintf(stderr, "GPU index must be non-negative\n");
        return 2;
    }
    cudaDeviceProp p{};
    cudaError_t result = cudaGetDeviceProperties(&p, index);
    if (result != cudaSuccess) {
        std::fprintf(stderr, "cudaGetDeviceProperties failed: %s\n", cudaGetErrorString(result));
        return 1;
    }
    // Device names normally contain no quotes; to guarantee JSON we omit name here.
    std::printf("{\"gpu_index\":%d,\"sm_count\":%d,\"l2_bytes\":%d,"
                "\"compute_capability\":\"%d.%d\",\"total_global_memory_bytes\":%llu}\n",
                index, p.multiProcessorCount, p.l2CacheSize,
                p.major, p.minor,
                static_cast<unsigned long long>(p.totalGlobalMem));
    return 0;
}
