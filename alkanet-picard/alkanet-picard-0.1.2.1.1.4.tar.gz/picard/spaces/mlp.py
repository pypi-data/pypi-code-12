genericLayer = {
    "type": "core.Dense",
    "options": {
        "output_dim": {
            "$choice": {
                "options": [256, 512, 1024]
            }
        }
    }
}

def get_space(input_dim,  output_dim):
    return {
        "layers": {
            "@merge": [
                [
                    {
                        "type": "core.Dense",
                        "options": {
                            "output_dim": 512,
                            "input_shape": [input_dim]
                        }
                    },
                    {
                        "type": "core.Activation",
                        "options": {
                            "activation": "relu"
                        }
                    },
                    {
                        "type": "core.Dropout",
                        "options": {
                            "p": {
                                "$uniform": {
                                    "low": 0,
                                    "high": 1
                                }
                            }
                        }
                    }
                ],
                {
                    "@repeat": {
                        "times": [1, 5],
                        "body": genericLayer
                    }
                },
                [
                    {
                        "type": "core.Dense",
                        "options": {
                            "output_dim": output_dim
                        }
                    },
                    {
                        "type": "core.Activation",
                        "options": {
                            "activation": "softmax"
                        }
                    }
                ]
            ]
        },
        "fit": {
            "batch_size": {
                "$choice": {
                    "options": [64, 128]
                }
            },
            "nb_epoch": 1
        }
    }
