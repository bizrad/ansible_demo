#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule
import lxml.etree as xmltree


def main():
    # Instantiate AnsibleModule
    module = AnsibleModule(
        argument_spec=dict(
            username=dict(required=True, type='str'),
            password=dict(required=True, type='str'),
            roles=dict(required=True, type='list')
        )
    )
    changed = False
    tree = xmltree.parse('/opt/tomcat/conf/tomcat-users.xml')
    root = tree.getroot()
    try:
        # Check that any roles are defined
        rolelist = list()
        for item in root.findall('{http://tomcat.apache.org/xml}role'):
            rolelist.append(item.attrib['rolename'])
        for role in module.params['roles']:
            if role not in rolelist:
                new_element = xmltree.SubElement(root, "{http://tomcat.apache.org/xml}role")
                new_element.set('rolename', role)
                changed = True
        # Check for updated info or no-op case
        for item in root.findall('{http://tomcat.apache.org/xml}user'):
            if item.attrib['username'] == module.params['username'] \
                    and item.attrib['password'] == module.params['password'] \
                    and item.attrib['roles'] == ','.join(module.params['roles']):
                # The data already exactly matches an entry, nothing to do
                if changed:
                    tree.write('/opt/tomcat/conf/tomcat-users.xml')
                module.exit_json(changed=changed, my_return_var='foo')
            elif item.attrib['username'] == module.params['username']:
                item.set('password', module.params['password'])
                item.set('roles', ','.join(module.params['roles']))
                tree.write('/opt/tomcat/conf/tomcat-users.xml')
                module.exit_json(changed=True, my_return_var="foo")

        # If we have not exited already add the new user
        new_element = xmltree.SubElement(root, "{http://tomcat.apache.org/xml}user")
        new_element.set('username', module.params['username'])
        new_element.set('password', module.params['password'])
        new_element.set('roles', ','.join(module.params['roles']))
        tree.write('/opt/tomcat/conf/tomcat-users.xml')
        module.exit_json(changed=True, my_return_var="foo")
    except (IndexError, KeyError):
        module.fail_json(msg="User XML file has malformed data.")


if __name__ == '__main__':
    main()
