test:
	echo "=== TESTE 0: ====================================================="
	./edlab-pdfconverter -i input.pdf -o output.pdf -d img -m '10 10 10 10'
	echo "=== TESTE 1: ====================================================="
	./edlab-pdfconverter -i input.pdf -o output1.pdf -d img1
	echo "=== TESTE 2: ====================================================="
	./edlab-pdfconverter -i input.pdf -o output2.pdf -d img2 -p 1-3
	echo "=== TESTE 3: ====================================================="
	./edlab-pdfconverter -i input.pdf -o output3.pdf -d img3 -p 1

clean:
	-rm output_images -rf
	-rm output[1-3].pdf
	-rm img -rf
	-rm img1 -rf
	-rm img2 -rf
	-rm img3 -rf
	-rm *pages*
