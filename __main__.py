import mawk

def main():
    if use_stdin_raw or use_stdin_py:  # TODO clean this up
        if args.s:
            for ri, raw in enumerate(record_iterator(sys.stdin, args.r)):
                if use_stdin_raw:
                    kept, transformed, reduced, formatted = process(raw, ri)
                    write_out(formatted)
                else:  # use_stdin_py
                    out = cmds((ri, eval(raw)))
                    p('out', out)
                    write_out(format_output(out))
        else:
            raw = sys.stdin.read()
            if use_stdin_raw:
                kept, transformed, reduced, formatted = process(raw)
                write_out(formatted)
            else:  # use_stdin_py
                out = cmds((None, eval(raw)))
                p('out', out)
                write_out(format_output(out))
    else:
        write_out(cmds(None))  # TODO is it going to be a problem that I'm passing a dummy arugment?


if __name__ == '__main__':
    main()
