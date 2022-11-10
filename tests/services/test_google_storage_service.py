from services.google_storage_service import init_google_storage


def test_google_storage_service_returns_google_storage_object_on_init(config):
    # arrange


    # act
    result = init_google_storage(config)

    # assert
    assert result.nifi_staging_bucket == nifi_staging_bucket
    assert result.log == log
    assert result.bucket == bucket
    assert result.storage_client == storage_client
