To use the push notification protocol plugin you must have a firebase project to send the notifications to and a service account json file with `Firebase Service Management Service Agent` roles.

In the project .env file you need to supply the information in the `Firebase Plugin Configuration` section.
> USE_FIREBASE_PLUGIN=true
FCM_PROJECT_ID=287275049656
FCM_NOTIFICATION_TITLE=You have important information in your digital wallet
FCM_NOTIFICATION_BODY=Please open your wallet
FCM_SERVICE_ACCOUNT={ flattend service account json }
FCM_MAX_SEND_RATE_MINUTES=5

* If `USE_FIREBASE_PLUGIN` is false it will not load the plugin.
* `FCM_PROJECT_ID` can be found in the firebase console
* `FCM_NOTIFICATION_TITLE` and `FCM_NOTIFICATION_BODY` is the information displayed in the push notification.
* `FCM_MAX_SEND_RATE_MINUTES` can be used for restricting the rate of notifications. Useful for when an external agent sends rapid basic messages. Setting to zero will have no restrictions and may result in notification spam type behavior.