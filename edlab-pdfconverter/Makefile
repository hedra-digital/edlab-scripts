test:
	echo "=== TESTE 1: ====================================================="
	./edlab-pdfconverter -i input.pdf -o output1.pdf -p 1-3 -d img -m '10 10 10 10'
	echo "=== TESTE 4: Juntar pdfs ========================================="
	./edlab-pdfconverter -i *.pdf -j  -o output2.pdf

clean:
	-rm output_images -rf
	-rm output[1-3].pdf
	-rm img -rf
	-rm img1 -rf
	-rm img2 -rf
	-rm img3 -rf
	-rm *pages* *merge*
