
#ifndef __MEM_CACHE_PREFETCH_TESTPF_HH__
#define __MEM_CACHE_PREFETCH_TESTPF_HH__

#include <string>
#include <unordered_map>
#include <vector>
#include <deque>
#include "base/types.hh"
#include "mem/cache/prefetch/queued.hh"
#include "mem/cache/replacement_policies/replaceable_entry.hh"
#include "mem/packet.hh"

struct TestPFParams;

class TestPF : public QueuedPrefetcher
{
  protected:

    const int degree;
    std::deque <Addr> iml;

    void notifyRetiredInst(const Addr pc);

    class PrefetchListenerPC : public ProbeListenerArgBase<Addr>
    {
      public:
        PrefetchListenerPC(TestPF &_parent, ProbeManager *pm, const std::string &name)
            : ProbeListenerArgBase(pm, name),
              parent(_parent) {}
        void notify(const Addr& pc) override;
      protected:
        TestPF &parent;
    };

    std::vector<PrefetchListenerPC *> listenersPC;

  public:
    TestPF(const TestPFParams *p);
    ~TestPF() override;

    void calculatePrefetch(const PrefetchInfo &pfi,
                           std::vector<AddrPriority> &addresses) override;

    void addEventProbeRetiredInsts(SimObject *obj, const char *name);
};

#endif // __MEM_CACHE_PREFETCH_STRIDE_HH__
