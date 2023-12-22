To use the push notification protocol plugin you must have a firebase project to send the notifications to and a service account json file with `Firebase Service Management Service Agent` roles.

In the project .env file you need to supply the information in the `Firebase Plugin Configuration` section.
> USE_FIREBASE_PLUGIN=true
FIREBASE_PROJECT_ID=287275049656
FIREBASE_NOTIFICATION_TITLE=You have important information in your digital wallet
FIREBASE_NOTIFICATION_BODY=Please open your wallet
FIREBASE_SERVICE_ACCOUNT={ flattend service account json }

* If `USE_FIREBASE_PLUGIN` is false it will not load the plugin.
* `FIREBASE_PROJECT_ID` can be found in the firebase console
* `FIREBASE_NOTIFICATION_TITLE` and `FIREBASE_NOTIFICATION_BODY` is the information displayed in the push notification.