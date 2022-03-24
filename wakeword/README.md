# Todo: 

## Make the voice assistant listen to "hey glados"

**hey_glados_model.net** has been trained to listen to "hey glados" wakeword using Secret Sauce AI's [Precise Wakeword Model Maker](https://github.com/secretsauceai/precise-wakeword-model-maker)
```
[{'minimum_loss_accuracy': {'epoch': 268, 'loss': 0.0486, 'acc': 0.9332, 'val_loss': 0.1807, 'val_acc': 0.7474, 'acc_difference': 0.18580000000000008}}, {'minimum_loss_val_accuracy': {'epoch': 221, 'loss': 0.0721, 'acc': 0.8969, 'val_loss': 0.1487, 'val_acc': 0.8079, 'acc_difference': 0.08900000000000008}}, {'training_data': {'wake_words': 500, 'not_wake_words': 1071, 'test_wake_words': 198, 'test_not_wake_words': 281}}]
```

1) Run the whole assistant in python virtual environment.
2) Turn the hey_glados_model.net (keras model?) into (tensorflow model?) pb file.
3) Implement [mycroft-precise engine](https://github.com/MycroftAI/mycroft-precise) or preferably [Precise Lite Runner](https://github.com/OpenVoiceOS/precise_lite_runner) using the trained "hey glados" model.
4) Make better model with more collected voice samples.