#import <Foundation/Foundation.h>
#import <Security/Security.h>

int main(){
    SecKeychainRef keychain = NULL;

    OSStatus status = SecKeychainOpen("my-keychain", &keychain);

    if (status == errSecSuccess) {
        printf("[OPEN] Success\n");
    } else {
        printf("[OPEN] error: %d\n", status);
        return 1;
    }

    status = SecKeychainLock(keychain);

    if (status == errSecSuccess) {
        printf("[Lock] Success\n");
    } else {
        printf("[Lock] error: %d\n", status);
    }
}
