#import <Foundation/Foundation.h>
#import <Security/Security.h>

int main(){
    SecKeychainRef keychain = NULL;

    OSStatus status = SecKeychainCreate("my-keychain", // pathName
                                        8,             // passwordLength
                                        "password",    // password
                                        FALSE,         // promptUser
                                        NULL,          // initialAccess
                                        &keychain);    // keychain

    if (status == errSecSuccess) {
        printf("Success\n");
    } else if (status == errSecDuplicateKeychain) {
        printf("errSecDuplicateKeychain: A keychain with the same name already exists.\n");
        return 1;
    } else {
        printf("error: %d\n", status);
        return 1;
    }

    CFRelease(keychain);
    return 0;
}
