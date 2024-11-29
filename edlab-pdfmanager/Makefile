install:
	-sudo cp edlab-pdfmanager /usr/local/bin
test:
	echo "=== TESTE 1: cropar, arrancar páginas, remover texto e converter para png ======="
	./edlab-pdfmanager -i input.pdf -o output1.pdf -p 1-3 -rt -d img -m '10 10 10 10'
	echo "=== TESTE 2: Juntar pdfs ========================================================"
	./edlab-pdfmanager -i input.pdf BLANK output1.pdf -j 
	echo "=== TESTE 3: Juntar pdfs ========================================================"
	./edlab-pdfmanager -i *.pdf --page-counter
	echo "=== TESTE 4: Extrair texto de pdfs =============================================="
	./edlab-pdfmanager -i inputB.pdf --extract-text
	echo "=== TESTE 5: Colocar uma marca d'água no texto =================================="
	./edlab-pdfmanager -i sample.pdf --watermark
	echo "=== TESTE 6: verificar as cores ================================================="
	./edlab-pdfmanager -i inputB.pdf --check-color
	echo "=== TESTE 7: contas as páginas =================================================="
	./edlab-pdfmanager -i inputB.pdf --page-counter


clean:
	-rm output.pdf
	-rm output_images -rf
	-rm output[1-3].pdf
	-rm img -rf
	-rm img1 -rf
	-rm img2 -rf
	-rm img3 -rf
	-rm PAGES.txt 
	-rm *pages* *merge* *extracted_* log.txt output* *_watermark*
