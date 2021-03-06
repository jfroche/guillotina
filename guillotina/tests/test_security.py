# -*- coding: utf-8 -*-
from guillotina.security.utils import get_principals_with_access_content
from guillotina.security.utils import get_roles_with_access_content
from guillotina.tests import utils
from guillotina.transactions import managed_transaction

import json


async def test_get_guillotina(container_requester):
    async with await container_requester as requester:
        response, status = await requester('GET', '/db/guillotina/@sharing')
        assert response['local']['prinrole']['root']['guillotina.ContainerAdmin'] == 'Allow'
        assert response['local']['prinrole']['root']['guillotina.Owner'] == 'Allow'


async def test_database_root_has_none_parent(container_requester):
    async with await container_requester as requester:
        # important for security checks to not inherit...
        request = utils.get_mocked_request(requester.db)
        root = await utils.get_root(request)
        assert root.__parent__ is None


async def test_set_local_guillotina(container_requester):
    async with await container_requester as requester:
        response, status = await requester(
            'POST',
            '/db/guillotina/@sharing',
            data=json.dumps({
                'prinperm': [{
                    'principal': 'user1',
                    'permission': 'guillotina.AccessContent',
                    'setting': 'AllowSingle'
                }]
            })
        )
        assert status == 200

        response, status = await requester(
            'POST',
            '/db/guillotina/',
            data=json.dumps({
                '@type': 'Item',
                'id': 'testing'
            })
        )
        assert status == 201

        response, status = await requester(
            'GET', '/db/guillotina/testing/@sharing')

        assert len(response['inherit']) == 1
        assert response['inherit'][0]['prinrole']['root']['guillotina.ContainerAdmin'] == 'Allow'
        assert response['inherit'][0]['prinrole']['root']['guillotina.Owner'] == 'Allow'
        assert 'Anonymous User' not in response['inherit'][0]['prinrole']
        assert response['inherit'][0]['prinperm']['user1']['guillotina.AccessContent'] == 'AllowSingle'  # noqa

        request = utils.get_mocked_request(requester.db)
        root = await utils.get_root(request)

        async with managed_transaction(request=request, abort_when_done=True):
            container = await root.async_get('guillotina')
            testing_object = await container.async_get('testing')

            # Check the access users/roles
            principals = get_principals_with_access_content(testing_object, request)
            assert principals == ['root']
            roles = get_roles_with_access_content(testing_object, request)
            assert roles == ['guillotina.Reader', 'guillotina.Reviewer', 'guillotina.Owner',
                             'guillotina.Editor', 'guillotina.ContainerAdmin']

        # Now we add the user1 with inherit on the container
        response, status = await requester(
            'POST',
            '/db/guillotina/@sharing',
            data=json.dumps({
                'prinperm': [{
                    'principal': 'user1',
                    'permission': 'guillotina.AccessContent',
                    'setting': 'Allow'
                }]
            })
        )

        root = await utils.get_root(request)

        async with managed_transaction(request=request, abort_when_done=True):
            # need to retreive objs again from db since they changed
            container = await root.async_get('guillotina')
            testing_object = await container.async_get('testing')
            principals = get_principals_with_access_content(testing_object, request)
            assert len(principals) == 2
            assert 'user1' in principals

        # Now we add the user1 with deny on the object
        response, status = await requester(
            'POST',
            '/db/guillotina/testing/@sharing',
            data=json.dumps({
                'prinperm': [{
                    'principal': 'user1',
                    'permission': 'guillotina.AccessContent',
                    'setting': 'Deny'
                }]
            })
        )
        # need to retreive objs again from db since they changed
        root = await utils.get_root(request)

        async with managed_transaction(request=request, abort_when_done=True):
            container = await root.async_get('guillotina')
            testing_object = await container.async_get('testing')
            principals = get_principals_with_access_content(testing_object, request)
            assert principals == ['root']
