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

    status = SecKeychainDelete(keychain);
    if (status == errSecSuccess) {
        printf("[DELETE] Success\n");
    } else {
        printf("[DELETE] error: %d\n", status);
        return 1;
    }

    CFRelease(keychain);
    return 0;
}
