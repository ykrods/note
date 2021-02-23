/**
 *  macOS のアプリで 相互 TLS 認証 する例
 *
 *  # Note
 *
 *  * 秘密鍵(クライアント認証で必要)は一度キーチェーンに入れないといけないらしい
 *    ( SecIdentity が必要なのだが、キーチェーン経由じゃないとインスタンスを生成できない
 *
 *  * macOS の場合、アプリ用にキーチェーンを作成できる(iOS ではできないので、コードが少し変わる)
 *  * IP アクセスの場合は ATS は作動しないらしい( 127.0.0.1 なので無視)
 *
 *  # 課題
 *
 *  * 使い終わったキーチェーンを消すタイミングが不明（逆に先に NSURLCredential を作っておく?)
 *  * パスワードをランダムにしちゃうと途中で落ちた時とかに消せなくなりそう??
 */

#import "ViewController.h"

#include <Security/Security.h>

@implementation ViewController

- (void)viewDidLoad {
    [super viewDidLoad];

    self.webView.navigationDelegate = self;
}

- (void)viewWillAppear {
    [super viewWillAppear];

    NSURL *url = [NSURL URLWithString:@"https://127.0.0.1/"];
    NSURLRequest *req = [[NSURLRequest alloc] initWithURL:url];
    [self.webView loadRequest: req];
}

- (void)setRepresentedObject:(id)representedObject {
    [super setRepresentedObject:representedObject];
}

- (void)webView:(WKWebView *)webView
didFailProvisionalNavigation:(WKNavigation *)navigation
      withError:(NSError *)error {
    NSLog(@"Error %@", error);
}

- (void)webView:(WKWebView *)webView
didReceiveAuthenticationChallenge:(nonnull NSURLAuthenticationChallenge *)challenge
completionHandler:(nonnull void (^)(NSURLSessionAuthChallengeDisposition, NSURLCredential * _Nullable))completionHandler
{
    NSURLProtectionSpace *space = challenge.protectionSpace;

    NSLog(@"AuthenticationMethod: %@", space.authenticationMethod);

    if (![space.host isEqual: @"127.0.0.1"]) {
        completionHandler(NSURLSessionAuthChallengeCancelAuthenticationChallenge, NULL);
        return;
    }

    // サーバ認証
    if ([space.authenticationMethod isEqual: NSURLAuthenticationMethodServerTrust]) {

        NSData *certData = [self serverCert];
        SecCertificateRef cert = SecCertificateCreateWithData(NULL, (__bridge CFDataRef)certData);

        NSArray *certs = @[(__bridge id _Nonnull)(cert)];
        OSStatus status = SecTrustSetAnchorCertificates(space.serverTrust, (__bridge CFArrayRef)certs);
        if (status != errSecSuccess) {
            NSLog(@"Fail to SecTrustSetAnchorCertificate: %d", status);
            completionHandler(NSURLSessionAuthChallengeCancelAuthenticationChallenge, NULL);
            return;
        }

        CFErrorRef errorRef = NULL;
        bool valid = SecTrustEvaluateWithError(space.serverTrust, &errorRef);

        if (!valid) {
            NSError *error = (__bridge NSError *)errorRef;
            NSLog(@"Error: %@", error);
            error = nil;
            if (errorRef != NULL) {
                CFRelease(errorRef);
            }
            completionHandler(NSURLSessionAuthChallengeCancelAuthenticationChallenge, NULL);
            return;
        }

        NSURLCredential *credential = [NSURLCredential credentialForTrust:space.serverTrust];
        completionHandler(NSURLSessionAuthChallengeUseCredential, credential);
        return;
    }

    // クライアント認証(サーバ認証と別に呼び出される)
    if ([space.authenticationMethod isEqual: NSURLAuthenticationMethodClientCertificate]) {
        NSString *keychain_path = @"my-app-keychain";
        NSString *keychain_password = @"password";

        SecKeychainRef keychainRef = NULL;
        OSStatus status = SecKeychainCreate(
            [keychain_path cStringUsingEncoding: NSUTF8StringEncoding],
            (UInt32)[keychain_password length],
            [keychain_password cStringUsingEncoding: NSUTF8StringEncoding],
            FALSE, // promptUser
            NULL,  // initialAccess
            &keychainRef
        );

        if (status != errSecSuccess) {
            // 同じパスのキーチェーンが存在する場合、開く
            NSLog(@"open keychain");
            status = SecKeychainOpen([keychain_path cStringUsingEncoding: NSUTF8StringEncoding], &keychainRef);
            // パスワードを入力してアンロックする
            // （アンロックしないとユーザにパスワード入力を求める
            SecKeychainUnlock(
                keychainRef,
                (UInt32)[keychain_password length],
                [keychain_password cStringUsingEncoding: NSUTF8StringEncoding],
                TRUE  // usePassword
            );

            if (status != errSecSuccess) {
                NSLog(@"Fail to open Keychain");
                completionHandler(NSURLSessionAuthChallengeCancelAuthenticationChallenge, NULL);
                return;
            }
        }

        NSData *p12 = [self p12Data];
        NSString *p12_passphrase = @"passphrase";

        SecItemImportExportKeyParameters keyParams;
        keyParams.passphrase    = (__bridge CFStringRef)p12_passphraze;
        keyParams.version       = SEC_KEY_IMPORT_EXPORT_PARAMS_VERSION;
        keyParams.keyUsage      = NULL;
        keyParams.keyAttributes = NULL;
        keyParams.accessRef     = NULL;
        keyParams.alertPrompt   = NULL;
        keyParams.alertTitle    = NULL;
        keyParams.flags         = 0;

        SecExternalFormat inputFormat = kSecFormatPKCS12;
        SecExternalItemType itemType = kSecItemTypeAggregate;

        __block CFArrayRef items = NULL;

        // SecPKCS12Import の方がより適切な感
        status = SecItemImport((CFDataRef)p12,
                               NULL,        // fileNameOrExtension
                               &inputFormat,
                               &itemType,
                               0,           // flags
                               &keyParams,
                               keychainRef, // importKeychain
                               &items);


        if (status == errSecSuccess && items && CFArrayGetCount(items)) {
            // .p12 ファイルに1つの鍵ペアしか入れてない前提
            SecIdentityRef identity = (SecIdentityRef) CFArrayGetValueAtIndex(items, 0);
            NSURLCredential *credential = [NSURLCredential credentialWithIdentity: identity
                                                                     certificates: NULL
                                                                      persistence: NSURLCredentialPersistenceForSession];
            completionHandler(NSURLSessionAuthChallengeUseCredential, credential);
            // XXX: テンポラリなキーチェーンのつもりなので使い終わったら消したいのだが、
            //      消すとハンドシェイクに失敗する? ので消すタイミングを考える必要がある
            //SecKeychainDelete(keychainRef);
            CFRelease(keychainRef);
            return;
        }
        //SecKeychainDelete(keychainRef);
        CFRelease(keychainRef);
    }

    NSLog(@"Cancel");
    completionHandler(NSURLSessionAuthChallengeCancelAuthenticationChallenge, NULL);
}

-(NSData *)serverCert {
    // データで取得する想定で書いているが、ファイルから読み込んでもいい
    // (PEM の場合はバウンダリを除く必要があるが
    NSString *str = @"...";
    return [[NSData alloc] initWithBase64EncodedString: str
                                               options:NSDataBase64DecodingIgnoreUnknownCharacters];
}
-(NSData *)p12Data {
    // データで取得する想定で書いているが、ファイルから読み込んでもいい
    NSString *str = @"...";
    return [[NSData alloc] initWithBase64EncodedString: str
                                               options: NSDataBase64DecodingIgnoreUnknownCharacters];
}

/**
 * オマケの PEM 形式の公開鍵・秘密鍵を読み込むサンプル
 */
- (void) loadCertsPEM: (NSString *)certString
{
    NSData *data = [certString dataUsingEncoding:NSUTF8StringEncoding];

    SecExternalFormat inputFormat = kSecFormatPEMSequence;
    SecExternalItemType itemType = kSecItemTypeCertificate;

    OSStatus status = SecItemImport((__bridge CFDataRef)data,
                                    NULL,         // fileNameOrExtension
                                    &inputFormat,
                                    &itemType,
                                    0,            // flags
                                    NULL,         // keyParams
                                    NULL,         // importKeychain
                                    &items);

    NSLog(@"%d", status);
    NSLog(@"items: %@", items);
}

-(void)loadKeyPEM: (NSString *)keyString
{
    NSData *keyData = [keyString dataUsingEncoding:NSUTF8StringEncoding];

    SecExternalFormat inputFormat = kSecFormatBSAFE;
    SecExternalItemType itemType = kSecItemTypePrivateKey;

    CFArrayRef items = NULL;
    OSStatus status = SecItemImport((__bridge CFDataRef)keyData,
                                    NULL,         // fileNameOrExtension
                                    &inputFormat,
                                    &itemType,
                                    0,            // flags
                                    NULL,         // keyParams
                                    NULL,         // importKeychain
                                    &items);
    NSLog(@"%d", status);
    NSLog(@"items: %@", items);
}

@end
