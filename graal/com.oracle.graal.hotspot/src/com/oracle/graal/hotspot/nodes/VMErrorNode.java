/*
 * Copyright (c) 2012, Oracle and/or its affiliates. All rights reserved.
 * DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER.
 *
 * This code is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License version 2 only, as
 * published by the Free Software Foundation.
 *
 * This code is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 * version 2 for more details (a copy is included in the LICENSE file that
 * accompanied this code).
 *
 * You should have received a copy of the GNU General Public License version
 * 2 along with this work; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 * Please contact Oracle, 500 Oracle Parkway, Redwood Shores, CA 94065 USA
 * or visit www.oracle.com if you need additional information or have any
 * questions.
 */
package com.oracle.graal.hotspot.nodes;

import com.oracle.graal.api.code.*;
import com.oracle.graal.api.meta.*;
import com.oracle.graal.compiler.gen.*;
import com.oracle.graal.compiler.target.*;
import com.oracle.graal.graph.*;
import com.oracle.graal.hotspot.*;
import com.oracle.graal.lir.*;
import com.oracle.graal.nodes.*;
import com.oracle.graal.nodes.type.*;
import com.oracle.graal.snippets.*;

/**
 * Causes the VM to exit with a description of the current Java location
 * and an optional {@linkplain Log#printf(String, long) formatted} error message specified.
 */
public final class VMErrorNode extends FixedWithNextNode implements LIRGenLowerable {

    @Input private ValueNode format;
    @Input private ValueNode value;

    public VMErrorNode(ValueNode format, ValueNode value) {
        super(StampFactory.forVoid());
        this.format = format;
        this.value = value;
    }

    @Override
    public void generate(LIRGenerator gen) {
        long vmErrorStub = HotSpotGraalRuntime.getInstance().getConfig().vmErrorStub;
        LIRFrameState state = gen.state();
        BytecodePosition pos = state.topFrame;
        String where = CodeUtil.append(new StringBuilder(100), pos).toString();
        Kind[] signature = new Kind[] {Kind.Object, Kind.Object, Kind.Long};
        gen.emitCall(vmErrorStub, Kind.Void, signature, true, Constant.forObject(where), gen.operand(format), gen.operand(value));
    }

    @SuppressWarnings("unused")
    @NodeIntrinsic
    public static void vmError(String format, long value) {
        throw new GraalInternalError("");
    }
}