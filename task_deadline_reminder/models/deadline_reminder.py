from datetime import datetime,date,timedelta 
from odoo import api, fields, models, _
import logging
import calendar 
from odoo.exceptions import except_orm, ValidationError
class DeadLineReminder(models.Model):
    _inherit = "res.users"


#1 Today Morning todo List
    @api.model
    def _cron_deadline_reminder_morning_self(self): 
        from datetime import datetime     
        today = datetime.now().date()
        current_day = today.weekday() 
        current_time = datetime.now() 
        public_holiday = self.env['resource.calendar.leaves'].search([('date_from', '<=', current_time.strftime('%Y-%m-%d 23:59:59')),('date_to', '>=', current_time.strftime('%Y-%m-%d 00:00:00'))])
        # Check if it's a holiday
        if public_holiday:
            return True
        # Check if it's a weekend (Saturday or Sunday)
        if current_day in [calendar.SATURDAY, calendar.SUNDAY]:
            return True  # Skip sending reminders on weekends
        
        # Get all users        

        # users = self.env['res.users'].search([])   
        users = self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_user').id),])
     
        for user in users:            
        # Find tasks assigned to the user   
            email_from = '"Odoobot" <support@technians.com>'         
            email_to = user.login
            name = user.name           
            formatted_date = today.strftime("%d-%m-%Y")
            tasks = self.env['project.task'].search([
            ('user_ids', 'in', [user.id]),
            ('date_deadline', '=', today),  # Make sure 'today' is defined
            ('is_closed', '=', False) # 'task_stages' should be a list of stage IDs
])

            if tasks:           
                email_content = f"Hi {name}<br> This email is to remind you that the tasks listed below are due today. <br><br><br>"            
                email_content += "<table style = 'font-size: 16px; color: rgb(34, 34, 34); background-color: #FFF;border-collapse: collapse;width: 100%;'>"              
                email_content += "<thead>"
                email_content += "<tr>"  
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;' > Task</th>"             
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Project</th>"             
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Deadline</th>"           
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Link </th>" 
                email_content += "</tr>"  
                email_content += "</thead>"     
                email_content += "<tbody>"     
                    
                for task in tasks:  
                    task_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    task_link = f"{task_url}/web#id={task.id}&view_type=form&model=project.task"            
                    email_content += "<tr>"         
                    email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {task.name} </td>"                        
                    email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {task.project_id.name} </td>" 
                    email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {task.date_deadline} </td>"       
                    email_content += f"<td style='padding: 7px;border: 1px solid #ddd;padding: 5px;text-align: center;'><a href='{task_link}' style='background-color: #743f74; height:24px; width:80px; color: white; padding-top:1px;border: none; border-radius: 5px;text-align: center; text-decoration: none;display: inline-block; font-size: 15px;'>View</a></td>"    
                    email_content += "</tr>" 
                            
                email_content += "</tbody>"     
                email_content += "</table>" 
                email_content += "<br>Kindly Complete the Tasks Today Itself !"
                # Send the email to the user            
                subject = f"{name} Your Today's Todo List - {formatted_date}" 
                mail_values = {                
                    'subject': subject,                
                    'body_html': email_content,  
                    'email_from': email_from,              
                    'email_to': email_to,            }          
                self.env['mail.mail'].create(mail_values).send()       
        return True
    

#2  Today Evening Pending todo List
    @api.model
    def _cron_deadline_reminder_evening_self(self):        
        from datetime import datetime        
        today = datetime.now().date()
        current_day = today.weekday() 
        current_time = datetime.now() 
        public_holiday = self.env['resource.calendar.leaves'].search([('date_from', '<=', current_time.strftime('%Y-%m-%d 23:59:59')),('date_to', '>=', current_time.strftime('%Y-%m-%d 00:00:00'))])
        # Check if it's a holiday
        if public_holiday:
            return True 
        # Check if it's a weekend (Saturday or Sunday)
        if current_day in [calendar.SATURDAY, calendar.SUNDAY]:
            return True  # Skip sending reminders on weekends
    # Get all users        
        # users = self.env['res.users'].search([])     
        users = self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_user').id),])
   
        for user in users:    
            employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
            if employee and employee.parent_id.user_id:
                employee_manager_email = employee.parent_id.user_id.login        
    # # Find tasks assigned to the user   
            email_from = '"Odoobot" <support@technians.com>'         
            email_to = user.login
            name = user.name         
            formatted_date = today.strftime("%d-%m-%Y")
            completed_tasks = self.env['project.task'].search([('user_ids', 'in', [user.id]),('date_deadline', '=', today),('is_closed', '=', True)])          
            pending_tasks = self.env['project.task'].search([('user_ids', 'in', [user.id]),('date_deadline', '=', today),('is_closed', '=', False)])          
            email_content = f"Hi {name} <br> Below is the Summary of Tasks you completed today. <br><br>"            
            email_content += "<p>Tasks Pending Today - " +str(len(pending_tasks))     
            if pending_tasks:  
                  
                email_content += "<table style = 'font-size: 16px; color: rgb(34, 34, 34); background-color: #FFF;border-collapse: collapse;width: 100%;'>"              
                email_content += "<thead>"
                email_content += "<tr>"  
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;' > Task</th>"             
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Project</th>"             
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Stage</th>"           
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Link </th>" 
                email_content += "</tr>"  
                email_content += "</thead>"     
                email_content += "<tbody>"     
                    
                for task in pending_tasks:  
                    if task.date_deadline:
                        deadline_date = fields.Datetime.from_string(task.date_deadline)
                        days_ago = (datetime.now() - deadline_date).days
                        days_ago_str = f"{days_ago} days ago"
                    else:
                        days_ago_str = "No deadline set"  # Handle case where deadline is not defined

                    task_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    task_link = f"{task_url}/web#id={task.id}&view_type=form&model=project.task"            
                    email_content += "<tr>"         
                    email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {task.name} </td>"                        
                    email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {task.project_id.name} </td>" 
                    email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {task.stage_id.name} </td>"       
                    email_content += f"<td style='padding: 7px;border: 1px solid #ddd;padding: 5px;text-align: center;'><a href='{task_link}' style='background-color: #743f74; height:24px; width:80px; color: white; padding-top:1px;border: none; border-radius: 5px;text-align: center; text-decoration: none;display: inline-block; font-size: 15px;'>View</a></td>"    
                    email_content += "</tr>" 
                email_content += "</tbody>"     
                email_content += "</table>" 
                email_content += "<br>Kindly Complete the Tasks Today Itself !"
            email_content += "<br><p>Tasks Completed Today - " + str(len(completed_tasks))
            if len(completed_tasks)>0:
                email_content += "<table style = 'font-size: 16px; color: rgb(34, 34, 34); background-color: #FFF;border-collapse: collapse;width: 100%;'>"              
                email_content += "<thead>"
                email_content += "<tr>"  
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;' > Task</th>"             
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Project</th>"             
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Stage</th>"           
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Link </th>" 
                email_content += "</tr>"  
                email_content += "</thead>"     
                email_content += "<tbody>" 
                for done_task in completed_tasks:
                    task_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    task_link = f"{task_url}/web#id={done_task.id}&view_type=form&model=project.task"
                    email_content += "<tr>"         
                    email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {done_task.name} </td>"                        
                    email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {done_task.project_id.name} </td>" 
                    email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {done_task.stage_id.name} </td>"       
                    email_content += f"<td style='padding: 7px;border: 1px solid #ddd;padding: 5px;text-align: center;'><a href='{task_link}' style='background-color: #743f74; height:24px; width:80px; color: white; padding-top:1px;border: none; border-radius: 5px;text-align: center; text-decoration: none;display: inline-block; font-size: 15px;'>View</a></td>"    
                    email_content += "</tr>" 
            email_content += "</tbody>"     
            email_content += "</table>" 
            
                # Send the email to the user  
            subject = f"{name} Your Today's Pending Todo List - {formatted_date}"          
            mail_values = {                
                'subject': subject,                
                'body_html': email_content,  
                'email_from': email_from,              
                'email_to': email_to,  
                'email_cc': employee_manager_email,          }          
            self.env['mail.mail'].create(mail_values).send()       
        return True
        
    
#3 Missing Deadline Reminder send mail to the admin
    def send_email_to_deadline_missing(self):
        current_datetime = datetime.now()  # Get the current date and time
        formatted_datetime = current_datetime.strftime("%d-%m-%Y ")  # Format it as per your requirement
        current_day = current_datetime.weekday() 
        current_time = datetime.now() 
        public_holiday = self.env['resource.calendar.leaves'].search([('date_from', '<=', current_time.strftime('%Y-%m-%d 23:59:59')),('date_to', '>=', current_time.strftime('%Y-%m-%d 00:00:00'))])
        # Check if it's a holiday
        if public_holiday:
            return True 
        # Check if it's a weekend (Saturday or Sunday)
        if current_day in [calendar.SATURDAY, calendar.SUNDAY]:
            return True  # Skip sending reminders on weekends
        users = self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_erp_manager').id),])

        for user in users:
            name = user.name
            tasks = self.env['project.task'].search([('date_deadline', '=', False),('is_closed', '=', False)]) 
            task_count = len(tasks)             
            subject = f'Tasks without Deadline - {formatted_datetime}'
            body= f'Hi {name}<br>'
            body+='This is to inform you that deadline is missing for these tasks. <br><br>   '    
            body += f'Total Task - {task_count} task <br><br>'    
            body += "<table style = 'font-size: 16px; color: rgb(34, 34, 34); background-color: #FFF;border-collapse: collapse;width: 100%;'>"             
            body += "<thead>"
            body += "<tr>"  
            body += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;' > Task</th>"             
            body += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Project</th>"                     
            body += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Link </th>" 
            body += "</tr>"  
            body += "</thead>"     
            body += "<tbody>" 
            for i, task in enumerate(tasks):
                if i >= 10:
                    break  # Exit the loop after processing 10 tasks
    
                deadline_missing = task.date_deadline
                if deadline_missing != datetime: 
                    task_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    task_link = f"{task_url}/web#id={task.id}&view_type=form&model=project.task"  
                    if task.project_id.name is False:
                        project_name = 'Unknown'
                    else:
                        project_name = task.project_id.name       
                    body += "<tr>"         
                    body += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {task.name} </td>"                         
                    body += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {project_name} </td>" 
                    body += f"<td style='padding: 7px;border: 1px solid #ddd;padding: 5px;text-align: center;'><a href='{task_link}' style='background-color: #743f74;color: white; padding: 6px 8px;border: none; border-radius: 5px;text-align: center; text-decoration: none;display: inline-block; font-size: 15px;'>View</a></td>"    
                    body += "</tr>"                           
            body += "</tbody>"     
            body += "</table>"
            task_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            action = self.env['ir.actions.act_window'].search([('name', '=', 'Task Without Deadline')], limit=1)
            menu = self.env['ir.ui.menu'].search([('name', '=', 'Overpassed Tasks')], limit=1)
            task_links = f"{task_url}/web#action={action.id}&model=project.task&view_type=list&cids=1&menu_id=351"
            body += f"<br><a href='{task_links}'style='background-color: #743f74; color: white; padding: 6px 8px;border: none; border-radius: 5px;text-align: center; text-decoration: none;display: inline-block; font-size: 15px;' >View All</a>"
            body += '<br><br><br>Please take necessary actions to address this issue. <br>' 
            email_values = {
                'subject': subject,
                'body_html': body,  # You can also use 'body' for plain text
                'email_to': user.login,
                'email_from': '"Odoobot" <support@technians.com>',
            }
            self.env['mail.mail'].create(email_values).send()
        return True


#4 overdue email send to the admin
    def send_email_overdue_to_all_admin(self):
        current_datetime = datetime.now()  # Get the current date and time
        formatted_datetime = current_datetime.strftime("%d-%m-%Y ")  # Format it as per your requirement
        current_day = current_datetime.weekday()  
        current_time = datetime.now() 
        public_holiday = self.env['resource.calendar.leaves'].search([('date_from', '<=', current_time.strftime('%Y-%m-%d 23:59:59')),('date_to', '>=', current_time.strftime('%Y-%m-%d 00:00:00'))])
        # Check if it's a holiday
        if public_holiday:
            return True
        # Check if it's a weekend (Saturday or Sunday)
        if current_day in [calendar.SATURDAY, calendar.SUNDAY]:
            return True  # Skip sending reminders on weekends
        users = self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_erp_manager').id),])

        for user in users:
            name = user.name
            tasks = self.env['project.task'].search([('date_deadline', '<', current_datetime),('date_deadline', '!=', False),('is_closed', '=', False)]) 
            task_count = len(tasks)  
            subject = f'Overdue Tasks  - {formatted_datetime}'
            body= f'Hi {name}<br>'
            body+='This is to inform you that the following tasks are Overdue. <br><br>   '    
            body += f'Total Tasks - {task_count} task <br><br>'    
            body += "<table style = 'font-size: 16px; color: rgb(34, 34, 34); background-color: #FFF;border-collapse: collapse;width: 100%;'>"             
            body += "<thead>"
            body += "<tr>"  
            body += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;' > Task</th>"             
            body += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Project</th>"                     
            body += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Link </th>" 
            body += "</tr>"  
            body += "</thead>"     
            body += "<tbody>" 
            for i, task in enumerate(tasks):
                if i >= 10:
                    break  # Exit the loop after processing 10 tasks
    
                deadline_passed = task.date_deadline
                if deadline_passed and deadline_passed != datetime.now().date(): 
                    task_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    task_link = f"{task_url}/web#id={task.id}&view_type=form&model=project.task"  
                    if task.project_id.name is False:
                            project_name = 'Unknown'
                    else:
                            project_name = task.project_id.name       
                    body += "<tr>"         
                    body += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {task.name} </td>"                         
                    body += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {project_name} </td>" 
                    body += f"<td style='padding: 7px;border: 1px solid #ddd;padding: 5px;text-align: center;'><a href='{task_link}' style='background-color: #743f74; color: white;     padding: 6px 8px; border: none; border-radius: 5px;text-align: center; text-decoration: none;display: inline-block; font-size: 15px;'>View</a></td>"    
                    body += "</tr>"                             
            body += "</tbody>"     
            body += "</table>"
            task_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            action = self.env['ir.actions.act_window'].search([('name', '=', 'Task Passed Deadline')], limit=1)
            task_links = f"{task_url}/web#action={action.id}&model=project.task&view_type=list&cids=1&menu_id=351"
            body += f"<br><a href='{task_links}'style='background-color: #743f74;color: white; padding: 6px 8px;border: none; border-radius: 5px;text-align: center; text-decoration: none;display: inline-block; font-size: 15px;' >View All</a>"
            body += '<br><br><br>Please take necessary actions to address this issue. <br>' 
            email_values = {
                'subject': subject,
                'body_html': body,  # You can also use 'body' for plain text
                'email_to': user.login,
                'email_from': '"Odoobot" <support@technians.com>',
            }
            self.env['mail.mail'].create(email_values).send()
        return True


#5 overdue email send to the specific users
    @api.model
    def send_email_overdue_to_specific_users(self):      
    # Get all users        
        current_datetime = datetime.now()  # Get the current date and time
        formatted_datetime = current_datetime.strftime("%d-%m-%Y ")  # Format it as per your requirement
        current_day = current_datetime.weekday() 
        current_time = datetime.now() 
        public_holiday = self.env['resource.calendar.leaves'].search([('date_from', '<=', current_time.strftime('%Y-%m-%d 23:59:59')),('date_to', '>=', current_time.strftime('%Y-%m-%d 00:00:00'))])
        # Check if it's a holiday
        if public_holiday:
            return True 
        # Check if it's a weekend (Saturday or Sunday)
        if current_day in [calendar.SATURDAY, calendar.SUNDAY]:
            return True  # Skip sending reminders on weekends
        # users = self.env['res.users'].search([])        
        users = self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_user').id),])

        for user in users:            
        # Find tasks assigned to the user   
            email_from = '"Odoobot" <support@technians.com>'         
            email_to = user.login
            name = user.name
            # today = datetime.now().date()
            # formatted_date = today.strftime("%d-%m-%Y")
            tasks = self.env['project.task'].search([('user_ids', 'in', [user.id]),('date_deadline', '<', current_datetime),('date_deadline', '!=', False),('is_closed', '=', False)]) 
            task_count = len(tasks)

            if tasks:           
                email_content = f"Hi {name}<br> This is to inform you that the following tasks are Overdue. <br><br>" 
                email_content += f'Total Tasks - {task_count} task <br><br><br>'            
                email_content += "<table style = 'font-size: 16px; color: rgb(34, 34, 34); background-color: #FFF;border-collapse: collapse;width: 100%;'>"              
                email_content += "<thead>"
                email_content += "<tr>"  
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;' > Task</th>"             
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Project</th>"             
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Deadline</th>"           
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Link </th>" 
                email_content += "</tr>"  
                email_content += "</thead>"     
                email_content += "<tbody>"     
                for i, task in enumerate(tasks):
                    if i >= 10:
                        break  # Exit the loop after processing 10 tasks

                    deadline_passed = task.date_deadline
                    if deadline_passed and deadline_passed != datetime.now().date():  
                        task_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        task_link = f"{task_url}/web#id={task.id}&view_type=form&model=project.task"   
                        if task.project_id.name is False:
                            project_name = 'Unknown'
                        else:
                            project_name = task.project_id.name          
                        email_content += "<tr>"         
                        email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {task.name} </td>"                        
                        email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {task.project_id.name} </td>" 
                        email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {task.date_deadline} </td>"       
                        email_content += f"<td style='padding: 7px;border: 1px solid #ddd;padding: 5px;text-align: center;'><a href='{task_link}' style='background-color: #743f74; height:24px; width:80px; color: white; padding-top:1px;border: none; border-radius: 5px;text-align: center; text-decoration: none;display: inline-block; font-size: 15px;'>View</a></td>"    
                        email_content += "</tr>" 
                            
                email_content += "</tbody>"     
                email_content += "</table>"
                task_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                action = self.env['ir.actions.act_window'].search([('name', '=', 'Task Passed Deadline for Specific users')], limit=1)
                task_links = f"{task_url}/web#action={action.id}&model=project.task&view_type=list&cids=1&menu_id=351"
                email_content += f"<br><a href='{task_links}'style='background-color: #743f74;color: white; padding: 6px 8px;border: none; border-radius: 5px;text-align: center; text-decoration: none;display: inline-block; font-size: 15px;' >View All</a>"
                email_content += '<br><br><br>Please take necessary actions to address this issue. <br>' 
                # Send the email to the user            
                subject = f"{name} Overdue Tasks  - {formatted_datetime}" 
                mail_values = {                
                    'subject': subject,                
                    'body_html': email_content,  
                    'email_from': email_from,              
                    'email_to': email_to,            }          
                self.env['mail.mail'].create(mail_values).send()       
        return True

#6 Tasks Pending Till Date
    @api.model
    def task_overdue_before_today(self):    
        
        hr_email = 'career@technians.com'    
    # Get all users        
        current_datetime = date.today()  # Get the current date and time
       
        yesterday_datetime = current_datetime - timedelta(days=1)
        
        formatted_datetime = current_datetime.strftime("%d-%m-%Y ")  # Format it as per your requirement
        current_day = current_datetime.weekday() 
        
        current_time = datetime.now() 
        
        public_holiday = self.env['resource.calendar.leaves'].search([('date_from', '<=', current_time.strftime('%Y-%m-%d 23:59:59')),('date_to', '>=', current_time.strftime('%Y-%m-%d 00:00:00')),])
        # Check if it's a holiday
        # if public_holiday:
        #     return True 
        # Check if it's a weekend (Saturday or Sunday)
        if current_day in [calendar.SATURDAY, calendar.SUNDAY]:
            return True  # Skip sending reminders on weekends
        # users = self.env['res.users'].search([])        
        users = self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_user').id),])
        
        # if users:
        for user in users:  
            employee_manager_email = ''
            employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
            if employee and employee.parent_id.user_id:
                employee_manager_email = employee.parent_id.user_id.login
                
                # raise ValidationError(employee_manager_user_id)  
                # manager_user_id = self.env['res.users'].search([('user_id', '=', user_id)], limit=1)


        # Find tasks assigned to the user   
            email_from = '"Odoobot" <support@technians.com>'         
            email_to = user.login
            name = user.name
            # today = datetime.now().date()
            # formatted_date = today.strftime("%d-%m-%Y")
            tasks = self.env['project.task'].search([('user_ids', 'in', [user.id]),('date_deadline', '<', yesterday_datetime),('date_deadline', '!=', False),('is_closed', '=', False)]) 
            task_count = len(tasks)
            
            if tasks:           
                email_content = f"Dear {name},<br> This mail is to remind you that there were pending tasks on your list that required completion.<br>Kindly provide clarification as to why you haven't been able to complete these tasks within the designated timeframe.<br><strong>Kindly note that if we do not receive clarification on the status of these tasks within 4 hours, by REPLYING TO THIS MAIL, your absence may be marked for yesterday.</strong><br>Your cooperation in this matter is greatly appreciated. If you have any questions or concerns, feel free to reach out to your reporting manager. <br><br>" 
                email_content += f'Total Tasks - {task_count} task <br><br><br>'            
                email_content += "<table style = 'font-size: 16px; color: rgb(34, 34, 34); background-color: #FFF;border-collapse: collapse;width: 100%;'>"              
                email_content += "<thead>"
                email_content += "<tr>"  
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;' > Task</th>"             
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Project</th>"             
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Deadline</th>"           
                email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Link </th>" 
                email_content += "</tr>"  
                email_content += "</thead>"     
                email_content += "<tbody>"     
                for i, task in enumerate(tasks):
                    if i >= 10:
                        break  # Exit the loop after processing 10 tasks

                    deadline_passed = task.date_deadline

                    if deadline_passed and deadline_passed != datetime.now().date():
                        # days_ago = (datetime.now() - deadline_date).days
                        # days_ago_str = f"{days_ago} days ago"  
                        task_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        task_link = f"{task_url}/web#id={task.id}&view_type=form&model=project.task"   
                        if task.project_id.name is False:
                            project_name = 'Unknown'
                        else:
                            project_name = task.project_id.name          
                        email_content += "<tr>"         
                        email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {task.name} </td>"                        
                        email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {task.project_id.name} </td>" 
                        email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {deadline_passed} </td>"       
                        email_content += f"<td style='padding: 7px;border: 1px solid #ddd;padding: 5px;text-align: center;'><a href='{task_link}' style='background-color: #743f74; height:24px; width:80px; color: white; padding-top:1px;border: none; border-radius: 5px;text-align: center; text-decoration: none;display: inline-block; font-size: 15px;'>View</a></td>"    
                        email_content += "</tr>" 
                            
                email_content += "</tbody>"     
                email_content += "</table>"



                task_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                # action = self.env['ir.actions.act_window'].search([('name', '=', 'Task Passed Deadline for Specific users')], limit=1)
                # task_links = f"{task_url}/web#action={action.id}&model=project.task&view_type=list&cids=1&menu_id=351"
                # email_content += f"<br><a href='{task_links}'style='background-color: #743f74;color: white; padding: 6px 8px;border: none; border-radius: 5px;text-align: center; text-decoration: none;display: inline-block; font-size: 15px;' >View All</a>"
                # email_content += '<br><br><br>Please take necessary actions to address this issue. <br>' 
                # Send the email to the user            
                subject = f"Attention! {name}: Pending Task & Yesterday Absence Clarification"

                # if task_count > 2:
                mail_values = {                
                    'subject': subject,                
                    'body_html': email_content,  
                    'email_from': email_from,              
                    'email_to': email_to,
                    'email_cc' : hr_email + ',' + str(employee_manager_email),
                    'reply_to' : hr_email
                                }          
                self.env['mail.mail'].create(mail_values).send()       
        return True

    #7 Upcoming Project Renewals 
    @api.model
    def project_renewal_reminder(self):    
        # Get all users        
        ten_days_later = date.today() + timedelta(days=10)
        users = self.env['res.users'].search([('groups_id', 'in', self.env.ref('project.group_project_manager').id),])
        active_projects = self.env['project.project'].search([
        ('stage_id.fold', '=', False),  # Ensure project stage is not closed
        ('active', '=', True),  # Ensure =project is active
        ('date', '<=',ten_days_later)
        ])       
        if len(active_projects) == 0:
            return True
        # raise ValidationError(len(active_projects)) 

        
        
            # Calculate the date 10 days from today
        
        email_content = f"This mail is to remind you that Renewal of the following Projects are Due<br><br>" 
        email_content += "<table style = 'font-size: 16px; color: rgb(34, 34, 34); background-color: #FFF;border-collapse: collapse;width: 100%;'>"              
        email_content += "<thead>"
        email_content += "<tr>"  
        email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;' > Project Name</th>"             
        email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Renewal Date</th>"             
        email_content += f"<th style='text-align: center; background-color:#743f74 !important;color: #fff;padding: 5px;'> Link </th>" 
        email_content += "</tr>"  
        email_content += "</thead>"     
        email_content += "<tbody>" 
         
        for project in active_projects:
            project_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            project_link = f"{project_url}/web#id={project.id}&view_type=form&model=project.project"
            if project.date and project.date <= ten_days_later:
                email_content += "<tr>"         
                email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {project.name or ''} </td>"                        
                email_content += f"<td style='border: 1px solid #ddd;padding: 5px;text-align: left; font-size: 15px;'> {project.date or ''} </td>"       
                email_content += f"<td style='padding: 7px;border: 1px solid #ddd;padding: 5px;text-align: center;'><a href='{project_link}' style='background-color: #743f74; height:24px; width:80px; color: white; padding-top:1px;border: none; border-radius: 5px;text-align: center; text-decoration: none;display: inline-block; font-size: 15px;'>View</a></td>"    
                email_content += "</tr>" 
                            
        email_content += "</tbody>"     
        email_content += "</table>"
        
        for user in users:
            subject = f"Attention! {user.name}: Project Renewals Pending"
                # if task_count > 2:
            email_from = '"Odoobot" <support@technians.com>'         
            email_to = user.login
            mail_values = {                
                'subject': subject,                
                'body_html': email_content,  
                'email_from': email_from,              
                'email_to': email_to,
                # 'reply_to' : hr_email
                            }   
            if not self.is_weekend_or_holiday(self,0):       
                self.env['mail.mail'].create(mail_values).send()       
        return True
            # raise ValidationError('renewal upcoming')  
        # if len(users)>0:
        #     for user in users:
    @staticmethod
    def is_weekend_or_holiday(self ,date_adjustment=0):
        today = fields.Date.today()

        if today.weekday() in [5, 6]:
            return True

        check_date = today + timedelta(days=date_adjustment)
        public_holiday_count = self.env['resource.calendar.leaves'].search_count([
            ('date_from', '<=', check_date),
            ('date_to', '>=', check_date)
        ])
        return public_holiday_count > 0    

            
        
