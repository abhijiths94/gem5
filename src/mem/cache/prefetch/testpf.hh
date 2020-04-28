
#ifndef __MEM_CACHE_PREFETCH_TESTPF_HH__
#define __MEM_CACHE_PREFETCH_TESTPF_HH__

#include <string>
#include <unordered_map>
#include <vector>

#include "base/types.hh"
#include "mem/cache/prefetch/queued.hh"
#include "mem/cache/replacement_policies/replaceable_entry.hh"
#include "mem/packet.hh"

struct TestPFParams;

class TestPF : public QueuedPrefetcher
{
  protected:

    const int degree;

  public:
    TestPF(const TestPFParams *p);
    ~TestPF() override;

    void calculatePrefetch(const PrefetchInfo &pfi,
                           std::vector<AddrPriority> &addresses) override;
};

#endif // __MEM_CACHE_PREFETCH_STRIDE_HH__
