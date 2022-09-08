graphgen: graph_gen.c graph_test.c
	gcc graph_gen.c graph_test.c -I/usr/local/include/igraph -c
	gcc graph_gen.o graph_test.o -L/usr/local/lib -ligraph -lm -o graph_test
smsgen: graph_gen.c sms_gen.c 
	gcc graph_gen.c sms_gen.c -I/usr/local/include/igraph -c -g
	gcc graph_gen.o sms_gen.o -L/usr/local/lib -ligraph -lm -o sms_gen
	# add test file for smsgen
attack: graph_gen.c sms_gen.c attack.c attack_test.c
	gcc graph_gen.c sms_gen.c attack.c attack_test.c -I/usr/local/include/igraph -c -g
	gcc graph_gen.o sms_gen.o attack.o attack_test.o -L/usr/local/lib -ligraph -lm -o attack_test