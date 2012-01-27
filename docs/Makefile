all: arch.png arch.html

arch.dot: arch.rst Makefile
	./rst2dot.py $< $@

arch.png: arch.dot Makefile
	dot -Tpng -o $@ $<

arch.html: arch.rst Makefile
	rst2html -t $< $@
