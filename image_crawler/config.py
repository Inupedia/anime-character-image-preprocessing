OUTPUT_CONFIG = {
    # verbose / simplified output
    "VERBOSE": False,
    "PRINT_ERROR": False,
}

NETWORK_CONFIG = {
    # proxy setting
    #   you should customize your proxy setting accordingly
    #   default is for clash
    "PROXY": {"https": "127.0.0.1:7890"},
    # common request header
    "HEADER": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
    },
}

USER_CONFIG = {
    # user id
    #   access your pixiv user profile to find this
    #   e.g. https://www.pixiv.net/users/xxxx
    "USER_ID": "25677044",
    "COOKIE": "first_visit_datetime_pc=2023-05-03+13%3A06%3A34; p_ab_id=4; p_ab_id_2=4; p_ab_d_id=1938885414; yuid_b=KAcZaRU; p_b_type=1; PHPSESSID=25677044_K7gPG7hLX1CT64fkVQj6edewGGYytc0k; device_token=26c0e69bc3b30e23c9757f4c01c56eff; c_type=30; privacy_policy_notification=0; a_type=0; b_type=1; QSI_S_ZN_5hF4My7Ad6VNNAi=v:0:0; login_ever=yes; privacy_policy_agreement=6; tag_view_ranking=Lt-oEicbBr~Ie2c51_4Sp~K8esoIs2eW~2En9amAT9s~pnCQRVigpy~wYgFTHA2CM~1LN8nwTqf_~oAnKp9i65M~0sdG-G1SOF~GdbSSnl725~Ged1jLxcdL~cryvQ5p2Tx~RTJMXD26Ak~75zhzbk0bS~RWSFf7r9Kc~VN7cgWyMmg~qcYo_5oqVP~0PxjkbsmdL~j6r9IfTnfX~CiSfl_AE0h~BvS4LEBHFe~zIv0cf5VVk~oBseebr-Be~RAl80sLAE_~3W7FUHC-JR~pnr0lxGjHI~Qa8ggRsDmW~UtvAYDyBtZ~kGYw4gQ11Z~9AgnrXtsDs; howto_recent_view_history=45362723; __cf_bm=nXisRr.pEWQ6lf0ce5H9yc87UoOsqKVUsHaeif5Fsyc-1687724155-0-ASKYOzoxBBSgOycy2QtCqWmSTtVlswTx+REsf/6oxv44N/s5rgqg4viC9m74hVDy4HezdTnRgb+n0xD0/SPPI6LUPjxszMuubQ0TS52zddDovitDNP2we8kuZ/OpRhmqUw==",
}


DOWNLOAD_CONFIG = {
    # image save path
    #   NOTE: DO NOT miss "/"
    "STORE_PATH": "./src/input/",
    # abort request / download
    #   after 10 unsuccessful attempts
    "N_TIMES": 10,
    # waiting time (s) after failure
    "FAIL_DELAY": 1,
    # max parallel thread number
    "N_THREAD": 12,
    # waiting time (s) after thread start
    "THREAD_DELAY": 1,
}
