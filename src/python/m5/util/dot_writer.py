# Copyright (c) 2012-2013,2019 ARM Limited
# All rights reserved.
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Andreas Hansson
#          Uri Wiener
#          Sascha Bischoff

#####################################################################
#
# System visualization using DOT
#
# While config.ini and config.json provide an almost complete listing
# of a system's components and connectivity, they lack a birds-eye
# view. The output generated by do_dot() is a DOT-based figure (as a
# pdf and an editable svg file) and its source dot code. Nodes are
# components, and edges represent the memory hierarchy: the edges are
# directed, from a master to slave. Initially all nodes are
# generated, and then all edges are added. do_dot should be called
# with the top-most SimObject (namely root but not necessarily), the
# output folder and the output dot source filename. From the given
# node, both processes (node and edge creation) is performed
# recursivly, traversing all children of the given root.
#
# pydot is required. When missing, no output will be generated.
#
#####################################################################

from __future__ import print_function
from __future__ import absolute_import

import m5, os, re
from m5.SimObject import isRoot, isSimObjectVector
from m5.params import PortRef, isNullPointer
from m5.util import warn
try:
    import pydot
except:
    pydot = False

def simnode_children(simNode):
    for child in simNode._children.values():
        if isNullPointer(child):
            continue
        if isSimObjectVector(child):
            for obj in child:
                if not isNullPointer(obj):
                    yield obj
        else:
            yield child

# need to create all nodes (components) before creating edges (memory channels)
def dot_create_nodes(simNode, callgraph):
    if isRoot(simNode):
        label = "root"
    else:
        label = simNode._name
    full_path = re.sub('\.', '_', simNode.path())
    # add class name under the label
    label = "\"" + label + " \\n: " + simNode.__class__.__name__ + "\""

    # each component is a sub-graph (cluster)
    cluster = dot_create_cluster(simNode, full_path, label)

    # create nodes per port
    for port_name in simNode._ports.keys():
        port = simNode._port_refs.get(port_name, None)
        if port != None:
            full_port_name = full_path + "_" + port_name
            port_node = dot_create_node(simNode, full_port_name, port_name)
            cluster.add_node(port_node)

    # recurse to children
    for child in simnode_children(simNode):
        dot_create_nodes(child, cluster)

    callgraph.add_subgraph(cluster)

# create all edges according to memory hierarchy
def dot_create_edges(simNode, callgraph):
    for port_name in simNode._ports.keys():
        port = simNode._port_refs.get(port_name, None)
        if port != None:
            full_path = re.sub('\.', '_', simNode.path())
            full_port_name = full_path + "_" + port_name
            port_node = dot_create_node(simNode, full_port_name, port_name)
            # create edges
            if isinstance(port, PortRef):
                if port.peer:
                    dot_add_edge(simNode, callgraph, full_port_name, port)
            else:
                for p in port.elements:
                    if p.peer:
                        dot_add_edge(simNode, callgraph, full_port_name, p)

    # recurse to children
    for child in simnode_children(simNode):
        dot_create_edges(child, callgraph)

def dot_add_edge(simNode, callgraph, full_port_name, port):
    peer = port.peer
    full_peer_path = re.sub('\.', '_', peer.simobj.path())
    full_peer_port_name = full_peer_path + "_" + peer.name

    # Each edge is encountered twice, once for each peer. We only want one
    # edge, so we'll arbitrarily chose which peer "wins" based on their names.
    if full_peer_port_name < full_port_name:
        dir_type = {
            (False, False) : 'both',
            (True,  False) : 'forward',
            (False, True)  : 'back',
            (True,  True)  : 'none'
        }[ (port.is_source,
            peer.is_source) ]
        edge = pydot.Edge(full_port_name, full_peer_port_name, dir=dir_type)
        callgraph.add_edge(edge)

def dot_create_cluster(simNode, full_path, label):
    # get the parameter values of the node and use them as a tooltip
    ini_strings = []
    for param in sorted(simNode._params.keys()):
        value = simNode._values.get(param)
        if value != None:
            # parameter name = value in HTML friendly format
            ini_strings.append(str(param) + "&#61;" +
                               simNode._values[param].ini_str())
    # join all the parameters with an HTML newline
    tooltip = "&#10;\\".join(ini_strings)

    return pydot.Cluster( \
                         full_path, \
                         shape = "Mrecord", \
                         label = label, \
                         tooltip = "\"" + tooltip + "\"", \
                         style = "\"rounded, filled\"", \
                         color = "#000000", \
                         fillcolor = dot_gen_colour(simNode), \
                         fontname = "Arial", \
                         fontsize = "14", \
                         fontcolor = "#000000" \
                         )

def dot_create_node(simNode, full_path, label):
    return pydot.Node( \
                         full_path, \
                         shape = "Mrecord", \
                         label = label, \
                         style = "\"rounded, filled\"", \
                         color = "#000000", \
                         fillcolor = dot_gen_colour(simNode, True), \
                         fontname = "Arial", \
                         fontsize = "14", \
                         fontcolor = "#000000" \
                         )

# an enumerator for different kinds of node types, at the moment we
# discern the majority of node types, with the caches being the
# notable exception
class NodeType:
    SYS = 0
    CPU = 1
    XBAR = 2
    MEM = 3
    DEV = 4
    OTHER = 5

# based on the sim object, determine the node type
def get_node_type(simNode):
    if isinstance(simNode, m5.objects.System):
        return NodeType.SYS
    # NULL ISA has no BaseCPU or PioDevice, so check if these names
    # exists before using them
    elif 'BaseCPU' in dir(m5.objects) and \
            isinstance(simNode, m5.objects.BaseCPU):
        return NodeType.CPU
    elif 'PioDevice' in dir(m5.objects) and \
            isinstance(simNode, m5.objects.PioDevice):
        return NodeType.DEV
    elif isinstance(simNode, m5.objects.BaseXBar):
        return NodeType.XBAR
    elif isinstance(simNode, m5.objects.AbstractMemory):
        return NodeType.MEM
    else:
        return NodeType.OTHER

# based on the node type, determine the colour as an RGB tuple, the
# palette is rather arbitrary at this point (some coherent natural
# tones), and someone that feels artistic should probably have a look
def get_type_colour(nodeType):
    if nodeType == NodeType.SYS:
        return (228, 231, 235)
    elif nodeType == NodeType.CPU:
        return (187, 198, 217)
    elif nodeType == NodeType.XBAR:
        return (111, 121, 140)
    elif nodeType == NodeType.MEM:
        return (94, 89, 88)
    elif nodeType == NodeType.DEV:
        return (199, 167, 147)
    elif nodeType == NodeType.OTHER:
        # use a relatively gray shade
        return (186, 182, 174)

# generate colour for a node, either corresponding to a sim object or a
# port
def dot_gen_colour(simNode, isPort = False):
    # determine the type of the current node, and also its parent, if
    # the node is not the same type as the parent then we use the base
    # colour for its type
    node_type = get_node_type(simNode)
    if simNode._parent:
        parent_type = get_node_type(simNode._parent)
    else:
        parent_type = NodeType.OTHER

    # if this node is the same type as the parent, then scale the
    # colour based on the depth such that the deeper levels in the
    # hierarchy get darker colours
    if node_type == parent_type:
        # start out with a depth of zero
        depth = 0
        parent = simNode._parent
        # find the closes parent that is not the same type
        while parent and get_node_type(parent) == parent_type:
            depth = depth + 1
            parent = parent._parent
        node_colour = get_type_colour(parent_type)
        # slightly arbitrary, but assume that the depth is less than
        # five levels
        r, g, b = map(lambda x: x * max(1 - depth / 7.0, 0.3), node_colour)
    else:
        node_colour = get_type_colour(node_type)
        r, g, b = node_colour

    # if we are colouring a port, then make it a slightly darker shade
    # than the node that encapsulates it, once again use a magic constant
    if isPort:
        r, g, b = map(lambda x: 0.8 * x, (r, g, b))

    return dot_rgb_to_html(r, g, b)

def dot_rgb_to_html(r, g, b):
    return "#%.2x%.2x%.2x" % (r, g, b)

# We need to create all of the clock domains. We abuse the alpha channel to get
# the correct domain colouring.
def dot_add_clk_domain(c_dom, v_dom):
    label = "\"" + str(c_dom) + "\ :\ " + str(v_dom) + "\""
    label = re.sub('\.', '_', str(label))
    full_path = re.sub('\.', '_', str(c_dom))
    return pydot.Cluster( \
                     full_path, \
                     shape = "Mrecord", \
                     label = label, \
                     style = "\"rounded, filled, dashed\"", \
                     color = "#000000", \
                     fillcolor = "#AFC8AF8F", \
                     fontname = "Arial", \
                     fontsize = "14", \
                     fontcolor = "#000000" \
                     )

def dot_create_dvfs_nodes(simNode, callgraph, domain=None):
    if isRoot(simNode):
        label = "root"
    else:
        label = simNode._name
    full_path = re.sub('\.', '_', simNode.path())
    # add class name under the label
    label = "\"" + label + " \\n: " + simNode.__class__.__name__ + "\""

    # each component is a sub-graph (cluster)
    cluster = dot_create_cluster(simNode, full_path, label)

    # create nodes per port
    for port_name in simNode._ports.keys():
        port = simNode._port_refs.get(port_name, None)
        if port != None:
            full_port_name = full_path + "_" + port_name
            port_node = dot_create_node(simNode, full_port_name, port_name)
            cluster.add_node(port_node)

    # Dictionary of DVFS domains
    dvfs_domains = {}

    # recurse to children
    for child in simnode_children(simNode):
        try:
            c_dom = child.__getattr__('clk_domain')
            v_dom = c_dom.__getattr__('voltage_domain')
        except AttributeError:
            # Just re-use the domain from above
            c_dom = domain
            v_dom = c_dom.__getattr__('voltage_domain')
            pass

        if c_dom == domain or c_dom == None:
            dot_create_dvfs_nodes(child, cluster, domain)
        else:
            if c_dom not in dvfs_domains:
                dvfs_cluster = dot_add_clk_domain(c_dom, v_dom)
                dvfs_domains[c_dom] = dvfs_cluster
            else:
                dvfs_cluster = dvfs_domains[c_dom]
            dot_create_dvfs_nodes(child, dvfs_cluster, c_dom)

    for key in dvfs_domains:
        cluster.add_subgraph(dvfs_domains[key])

    callgraph.add_subgraph(cluster)

def do_dot(root, outdir, dotFilename):
    if not pydot:
        return
    # * use ranksep > 1.0 for for vertical separation between nodes
    # especially useful if you need to annotate edges using e.g. visio
    # which accepts svg format
    # * no need for hoizontal separation as nothing moves horizonally
    callgraph = pydot.Dot(graph_type='digraph', ranksep='1.3')
    dot_create_nodes(root, callgraph)
    dot_create_edges(root, callgraph)
    dot_filename = os.path.join(outdir, dotFilename)
    callgraph.write(dot_filename)
    try:
        # dot crashes if the figure is extremely wide.
        # So avoid terminating simulation unnecessarily
        callgraph.write_svg(dot_filename + ".svg")
        callgraph.write_pdf(dot_filename + ".pdf")
    except:
        warn("failed to generate dot output from %s", dot_filename)

def do_dvfs_dot(root, outdir, dotFilename):
    if not pydot:
        return

    # There is a chance that we are unable to resolve the clock or
    # voltage domains. If so, we fail silently.
    try:
        dvfsgraph = pydot.Dot(graph_type='digraph', ranksep='1.3')
        dot_create_dvfs_nodes(root, dvfsgraph)
        dot_create_edges(root, dvfsgraph)
        dot_filename = os.path.join(outdir, dotFilename)
        dvfsgraph.write(dot_filename)
    except:
        warn("Failed to generate dot graph for DVFS domains")
        return

    try:
        # dot crashes if the figure is extremely wide.
        # So avoid terminating simulation unnecessarily
        dvfsgraph.write_svg(dot_filename + ".svg")
        dvfsgraph.write_pdf(dot_filename + ".pdf")
    except:
        warn("failed to generate dot output from %s", dot_filename)
