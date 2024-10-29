install:
	-sudo cp edlab-pdfconverter /usr/local/bin
test:
	echo "=== TESTE 1: cropar, arrancar páginas, remover texto e converter para png ======="
	./edlab-pdfconverter -i input.pdf -o output1.pdf -p 1-3 -rt -d img -m '10 10 10 10'
	echo "=== TESTE 2: Juntar pdfs ========================================================"
	./edlab-pdfconverter -i input.pdf BLANK output1.pdf -j 
	echo "=== TESTE 3: Juntar pdfs ========================================================"
	./edlab-pdfconverter -i *.pdf --page-counter
	echo "=== TESTE 4: Extrair texto de pdfs ========================================================"
	./edlab-pdfconverter -i inputB.pdf --extract-text

clean:
	-rm output.pdf
	-rm output_images -rf
	-rm output[1-3].pdf
	-rm img -rf
	-rm img1 -rf
	-rm img2 -rf
	-rm img3 -rf
	-rm PAGES.txt 
	-rm *pages* *merge* *extracted_text.txt
