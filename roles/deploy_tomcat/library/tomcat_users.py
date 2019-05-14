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
    add_new_user = False
    tree = xmltree.parse('/opt/tomcat/conf/tomcat-users.xml')
    root = tree.getroot()
    user_list = list()
    try:
        # Create a list of dictionaries for each user item
        for item in root.findall('user'):
            item_dict = dict()
            item_dict['xmltext'] = item.text
            for text_content in item.text.split():
                item_dict[text_content.split('=')[0]] = text_content.split('=')[1]
            user_list.append(item_dict)
        # Compare our input user to the current data
        for user_dict in user_list:
            if user_dict["username"] == module.params['username'] \
                    and user_dict["password"] == module.params['password'] \
                    and user_dict["roles"] == module.params['roles']:
                # The data already exactly matches an entry, nothing to do
                module.exit_json(changed=changed, my_return_var="foo")
            elif user_dict["username"] == module.params['username']:
                # Remove the entry matching user_dict['xmltext']

                pass
        # Add the line with our new data in
        changed = True
        xmltree.SubElement(root, "user").text = 'username="{0}" password="{1}" roles="{2}"' \
            .format(module.params['username'], module.params['password'], ",".join(module.params['roles']))
    except (IndexError, KeyError):
        module.fail_json(msg="User XML file has malformed data.")



    module.exit_json(changed=changed, my_return_var="foo")

if __name__ == '__main__':
    main()
