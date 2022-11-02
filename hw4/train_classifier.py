import os
import argparse
from os import environ
from da_classifier import IntentSlotClassifier

environ["KERAS_BACKEND"] = "plaidml.keras.backend"


parser = argparse.ArgumentParser()
# These arguments will be set appropriately by ReCodEx, even if you change them.
parser.add_argument("--batch_size", default=32, type=int, help="Batch size.")
parser.add_argument("--dropout", default=0.0, type=float,
                    help="Dropout regularization.")
parser.add_argument("--epochs", default=10, type=int, help="Number of epochs.")
parser.add_argument(
    "--hidden_layers", default=[800, 800, 800, 800], nargs="*", type=int, help="Hidden layer sizes.")
parser.add_argument("--l2", default=0.0, type=float,
                    help="L2 regularization.")
parser.add_argument("--label_smoothing", default=0.0,
                    type=float, help="Label smoothing.")
parser.add_argument("--embed_size", default=50,
                    type=int, help="Embed size.")
parser.add_argument("--learning_rate", default=0.001,
                    type=float, help="Learning rate.")
parser.add_argument("--activation_function", default="relu",
                    type=str, help="Activation function.")
parser.add_argument("--batch_normalization", default=True,
                    type=bool, help="Set batch normalization.")
parser.add_argument("--seed", default=42, type=int, help="Random seed.")
parser.add_argument("--threads", default=16, type=int,
                    help="Maximum number of threads to use.")


def main(args):

    model = IntentSlotClassifier(learning_rate=args.learning_rate,
                                 batch_size=args.batch_size,
                                 l2=args.l2, seed=args.seed,
                                 activation_function=args.activation_function,
                                 batch_normalization=args.batch_normalization,
                                 threads=args.threads,
                                 hidden_layers=args.hidden_layers,
                                 label_smoothing=args.label_smoothing,
                                 dropout=args.dropout
                                 )

    model.train(epochs=args.epochs)
    model.predict_file()
    print(model.predict("I want chinese food"))
    print(model.predict("chines "))
    print(model.predict("chine"))
    print(model.predict("italian"))
    print(model.predict("italia"))
    print(model.predict("persian restaurant in the north part of town"))
    print(model.predict("chinese food"))


if __name__ == "__main__":
    args = parser.parse_args([] if "__file__" not in globals() else None)
    main(args)
