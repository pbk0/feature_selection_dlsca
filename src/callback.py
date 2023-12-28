import keras as ke


class EarlyStopping(ke.callbacks.EarlyStopping):
    """
    This is custom call back to ensure best weights are restored at the end of training
    Note that default keras provided callback does not do that
    """
    
    def on_train_end(self, logs=None):
        super().on_train_end(logs=logs)
        self.model.set_weights(self.best_weights)
        
    