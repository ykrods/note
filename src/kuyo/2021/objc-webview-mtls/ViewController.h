#import <Cocoa/Cocoa.h>
#import <WebKit/WebKit.h>

@interface ViewController : NSViewController <WKNavigationDelegate>

@property  (nonatomic, weak) IBOutlet WKWebView *webView;

@end
