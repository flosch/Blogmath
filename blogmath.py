# -*- coding: utf-8 -*-

import sys
import interpreter

def main():
    print "Blogmath-Interpreter"
    
    if len(sys.argv) > 1:
        # Execute file
        filenames = sys.argv[1:]
        print "Executing %s..." % ", ".join(filenames)
        
        c = interpreter.Context()
        
        for filename in filenames:
            buf = open(filename).read()
            for _ in interpreter.evaluate(buf, c):
                pass
    else:
        # Start REPL interface
        print "('quit' or CTRL-C to terminate)"
        c = interpreter.Context()
        try:
            while True:
                try:
                    s = raw_input("> ")
                except EOFError:
                    print
                    continue

                if s == "quit":
                    break
                
                for output in interpreter.evaluate(s, c):
                    print output
        except KeyboardInterrupt:
            pass

if __name__ == "__main__": main()
