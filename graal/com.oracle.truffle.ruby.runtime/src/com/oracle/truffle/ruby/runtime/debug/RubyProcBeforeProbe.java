/*
 * Copyright (c) 2013 Oracle and/or its affiliates. All rights reserved. This
 * code is released under a tri EPL/GPL/LGPL license. You can use it,
 * redistribute it and/or modify it under the terms of the:
 *
 * Eclipse Public License version 1.0
 * GNU General Public License version 2
 * GNU Lesser General Public License version 2.1
 */
package com.oracle.truffle.ruby.runtime.debug;

import com.oracle.truffle.api.frame.*;
import com.oracle.truffle.api.nodes.*;
import com.oracle.truffle.ruby.runtime.*;
import com.oracle.truffle.ruby.runtime.core.*;

/**
 * A probe for instrumenting a Ruby program with a Ruby procedure to run before a call.
 */
public final class RubyProcBeforeProbe extends RubyProbe {

    private final RubyProc proc;

    public RubyProcBeforeProbe(RubyContext context, RubyProc proc) {
        super(context);
        this.proc = proc;
    }

    @Override
    public void enter(Node astNode, VirtualFrame frame) {
        proc.call(frame.pack());
    }

}