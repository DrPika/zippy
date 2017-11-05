/*
 * Copyright (c) 2013, Regents of the University of California
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
package edu.uci.python.runtime;

import java.util.*;

import com.oracle.truffle.api.nodes.*;

import edu.uci.python.nodes.ModuleNode;
import edu.uci.python.runtime.standardtype.*;

public class PythonParseResult {

    private final PythonModule module;
    private final RootNode rootNode;
    private final PythonContext context;

    private final Map<String, RootNode> functions;

    public PythonParseResult(PythonModule module, ModuleNode moduleNode, PythonContext context, Map<String, RootNode> functions) {
        this.module = module;
        this.rootNode = moduleNode;
        this.context = context;
        this.functions = functions;
    }

    public PythonModule getModule() {
        return module;
    }

    public RootNode getModuleRoot() {
        return rootNode;
    }

    public PythonContext getContext() {
        return context;
    }

    public RootNode getFunctionRoot(String functionName) {
        RootNode root = functions.get(functionName);
        assert root != null;
        return root;
    }

    public Collection<RootNode> getFunctionRoots() {
        return functions.values();
    }

    public void printAST() {

        if (PythonOptions.PrintASTFilter == null || "module".contains(PythonOptions.PrintASTFilter)) {
            printSeparationLine("module");
            NodeUtil.printCompactTree(System.out, rootNode);
        }

        for (String functionName : functions.keySet()) {

            if (PythonOptions.PrintASTFilter != null && !functionName.contains(PythonOptions.PrintASTFilter)) {
                continue;
            }

            printSeparationLine(functionName);
            RootNode root = functions.get(functionName);
            NodeUtil.printCompactTree(System.out, root);
        }
    }

    private static void printSeparationLine(String id) {
        // CheckStyle: stop system..print check
        System.out.println(" ------------- " + id + " ------------- ");
        // CheckStyle: resume system..print check
    }

    public void visualizeToNetwork() {
        boolean verbose = PythonOptions.VisualizedASTverbose;
        String rootStr = verbose ? NodeUtil.printTreeToString(rootNode) : NodeUtil.printCompactTreeToString(rootNode);
        System.out.println(rootStr);

        for (String functionName : functions.keySet()) {
            RootNode froot = functions.get(functionName);
            String frootStr = verbose ? NodeUtil.printTreeToString(froot) : NodeUtil.printCompactTreeToString(froot);
            System.out.println(frootStr);
        }
    }
}
