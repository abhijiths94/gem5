
#include "mem/cache/prefetch/testpf.hh"

#include <cassert>

#include "base/intmath.hh"
#include "base/logging.hh"
#include "base/random.hh"
#include "base/trace.hh"
#include "debug/HWPrefetch.hh"
#include "mem/cache/replacement_policies/base.hh"
#include "params/TestPF.hh"


TestPF::TestPF(const TestPFParams *p)
    : QueuedPrefetcher(p),
      degree(p->degree)
{
    printf("TESTPF !!!! Creating TestPF prefetcher ..........................\n");
}

void
TestPF::calculatePrefetch(const PrefetchInfo &pfi,
                                    std::vector<AddrPriority> &addresses)
{
    if (!pfi.hasPC()) {
        DPRINTF(HWPrefetch, " TESTPF !!!! Ignoring request with no PC.\n");
        return;
    }


    // Get required packet info
    Addr pf_addr = pfi.getAddr();
    Addr pc = pfi.getPC();

    DPRINTF(HWPrefetch, "TESTPF !!!! Calc Pref called : PC %x pkt_addr %x \n", pc, pf_addr);

    for (int d = 1; d <= degree; d++) {
        Addr new_addr = pf_addr + d * blkSize;
        DPRINTF(HWPrefetch, "TESTPF !!!! Calling pushback : pkt_addr %x \n", new_addr);

        addresses.push_back(AddrPriority(new_addr, 0));
    }
}

TestPF*
TestPFParams::create()
{
    return new TestPF(this);
}

TestPF::~TestPF()
{
    printf("Calling destructor ...... !!!!!!");
}
