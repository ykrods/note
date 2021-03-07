# Makefile
CC=gcc
CFLAGS=-Wall
FRAMEWORKS=-framework Foundation -framework Security
TARGETS=keychain-create keychain-delete keychain-getstatus keychain-item-add keychain-item-delete keychain-item-list keychain-item-retrieve keychain-lock keychain-unlock

all: $(TARGETS)

%: %.m
	$(CC) $^ -o build/$@ -lobjc -fobjc-arc $(FRAMEWORKS) $(CFLAGS)
