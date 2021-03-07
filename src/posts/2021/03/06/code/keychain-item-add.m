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

    NSDictionary *query = @{
        (__bridge id)kSecValueData: [@"password" dataUsingEncoding: NSUTF8StringEncoding],
        (__bridge id)kSecClass: (__bridge id)kSecClassGenericPassword,
        (__bridge id)kSecUseKeychain: (__bridge id)keychain,
        (__bridge id)kSecAttrLabel: @"label1", // 名前
        (__bridge id)kSecAttrAccount: @"account1",
        (__bridge id)kSecAttrService: @"service1",
    };
    status = SecItemAdd((__bridge CFDictionaryRef)query, NULL);

    if (status == errSecSuccess) {
        printf("[SecItemAdd] Success\n");
    } else {
        printf("[SecItemAdd] error: %d\n", status);
    }

    CFRelease(keychain);
}
