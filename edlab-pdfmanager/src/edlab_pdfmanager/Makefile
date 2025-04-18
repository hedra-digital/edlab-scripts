install:
	-sudo cp edlab-pdfmanager /usr/local/bin
test:
	echo "=== TESTE 1: cropar, arrancar páginas, remover texto e converter para png ======="
	python edlab-pdfmanager.py -i input.pdf -o output1.pdf -p 1-3 -rt -d img -m '10 10 10 10'
	echo "=== TESTE 2: Juntar pdfs ========================================================"
	python edlab-pdfmanager.py -i input.pdf BLANK output1.pdf -j 
	echo "=== TESTE 3: Juntar pdfs ========================================================"
	python edlab-pdfmanager.py -i *.pdf --page-counter
	echo "=== TESTE 4: Extrair texto de pdfs =============================================="
	python edlab-pdfmanager.py -i inputB.pdf --extract-text
	echo "=== TESTE 5: Colocar uma marca d'água no texto =================================="
	python edlab-pdfmanager.py -i sample.pdf --watermark
	echo "=== TESTE 6: verificar as cores ================================================="
	python edlab-pdfmanager.py -i inputB.pdf --check-color
	echo "=== TESTE 7: contas as páginas =================================================="
	python edlab-pdfmanager.py -i inputB.pdf --page-counter
	echo "=== TESTE 8: shrink ============================================================="
	python edlab-pdfmanager.py -i inputB.pdf --shrink
	echo "=== TESTE 9: convert-to-black ==================================================="
	python edlab-pdfmanager.py -i input.pdf --convert-to-black
	echo "=== TESTE 10: convert-to-gray ==================================================="
	python edlab-pdfmanager.py -i input.pdf --convert-to-gray
	echo "=== TESTE 11: extract-to-docx ==================================================="
	python edlab-pdfmanager.py -i inputB.pdf --extract-to-docx



clean:
	-rm output.pdf
	-rm output_images -rf
	-rm output[1-3].pdf
	-rm img -rf
	-rm img1 -rf
	-rm img2 -rf
	-rm img3 -rf
	-rm PAGES.txt 
	-rm *pages* *merge* *extracted_* log.txt output* *_watermark* *compressed* *modified* *.docx *gray* *black*
