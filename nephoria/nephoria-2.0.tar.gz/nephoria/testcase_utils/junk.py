
        parser.add_argument('--clc',
                                help="Address of Machine hosting CLC services",
                                default=None)

        parser.add_argument('--freeze-on-exit', dest='freeze_on_exit', action='store_true',
                                help="Freeze test without running clean methods at exit",
                                default=False)

        parser.add_argument('--emi',
                            help="pre-installed emi id which to execute these nephoria_unit_tests against",
                            default=None)

        parser.add_argument('--credpath',
                            help="path to credentials", default=None)

        parser.add_argument('--password',
                            help="Password to use for machine root ssh access", default=None)

        parser.add_argument('--nephoria_unit_tests', nargs='+',
                            help="test cases to be executed", default=[])

        parser.add_argument('--keypair',
                            help="Keypair to use in this test", default=None)

        parser.add_argument('--zone',
                            help="Zone to use in this test", default=None)

        parser.add_argument('--vmtype',
                            help="Virtual Machine Type to use in this test",
                            default='c1.medium')

        parser.add_argument('--user-data',
                            help="User data string to provide instance run within this test",
                            default=None)

        parser.add_argument('--instance-user',
                            help="Username used for ssh login. Default:'root'", default='root')

        parser.add_argument('--instance-password',
                            help="Password used for ssh login. When value is 'None' ssh "
                                 "keypair will be used and not username/password, "
                                 "default:'None'",
                            default=None)


        parser.add_argument('--region',
                            help="Use AWS region instead of Eucalyptus", default=None)

        parser.add_argument('--use-color', dest='use_color', action='store_true',
                            default=False)

        parser.add_argument('--log-level',
                            help="log level for stdout logging", default='debug')

        parser.add_argument('--logfile',
                            help="file path to log to (in addtion to stdout", default=None)

        parser.add_argument('--logfile-level',
                            help="log level for log file logging", default='debug')
        parser.add_argument('--html-anchors', dest='html_anchors', action='store_true',
                        help="Print HTML anchors for jumping through test results",
                        default=False)