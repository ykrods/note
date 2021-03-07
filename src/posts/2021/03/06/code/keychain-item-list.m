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
        (__bridge id)kSecClass: (__bridge id)kSecClassGenericPassword,
        // https://developer.apple.com/forums/thread/95762
        (__bridge id)kSecMatchSearchList: @[ (__bridge id)keychain ],
        (__bridge id)kSecReturnAttributes: @YES,
        (__bridge id)kSecMatchLimit: (__bridge id)kSecMatchLimitAll
    };
    CFTypeRef result = NULL;
    status = SecItemCopyMatching((__bridge CFDictionaryRef)query, &result);

    if (status == errSecSuccess) {
        printf("[SecItemCopyMatching] Success\n");

        NSArray *ary = (__bridge_transfer NSArray *)result;
        printf("Search result: %ld\n", [ary count]);
        for (NSDictionary *item in ary) {
            NSLog(@"%@", item);
        }
        // CFRelease(result);

    } else if (status == errSecItemNotFound) {
        printf("[SecItemCopyMatching] NotFound\n");
    } else {
        printf("[SecItemCopyMatching] error: %d\n", status);
    }

    CFRelease(keychain);
}
