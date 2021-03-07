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

    SecKeychainStatus keychainStatus = 0;
    status = SecKeychainGetStatus(keychain, &keychainStatus);
    if (status == errSecSuccess) {
        printf("[GetStatus] Success\n");

        // 定数が 1,2,4 で、 GetStatus の戻り値が 7 とかなので多分ビット列なんだと
        // 思われるが、ドキュメントに書いてない
        if (keychainStatus & kSecUnlockStateStatus) {
            printf("unlocked\n");
        }
        if (keychainStatus & kSecReadPermStatus) {
            printf("readable\n");
        }
        if (keychainStatus & kSecWritePermStatus) {
            printf("writable\n");
        }
    } else {
        printf("[GetStatus] error: %d\n", status);
    }
}
