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

    status = SecKeychainUnlock(keychain, 8, "password", TRUE);

    if (status == errSecSuccess) {
        printf("[Unlock] Success\n");
    } else {
        printf("[Unlock] error: %d\n", status);
    }
}
