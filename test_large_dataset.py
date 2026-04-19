from app import app, db, Hospital, Donor, Recipient
import pandas as pd

with app.app_context():
    # Read the large dataset
    df = pd.read_excel('neurobridge_large_dataset.xlsx')
    print(f'Excel file loaded with {len(df)} rows')
    print('Columns:', list(df.columns))
    print()
    
    # Get initial counts
    initial_hospitals = len(Hospital.query.all())
    initial_donors = len(Donor.query.all())
    initial_recipients = len(Recipient.query.all())
    print(f'Database initial state: {initial_hospitals} hospitals, {initial_donors} donors, {initial_recipients} recipients')
    print()
    
    hospitals_created = 0
    donors_added = 0
    recipients_added = 0
    errors = []
    
    for index, row in df.iterrows():
        try:
            hospital_name = str(row['hospital']).strip()
            if not hospital_name:
                errors.append(f"Row {index+1}: Missing hospital name")
                continue
            
            # Check if hospital exists
            hospital = Hospital.query.filter_by(name=hospital_name).first()
            
            # Auto create hospital if it doesn't exist
            if not hospital:
                email = f"{hospital_name.lower().replace(' ', '')}@neurobridge.com"
                # Check if email already exists
                existing_email = Hospital.query.filter_by(email=email).first()
                if existing_email:
                    email = f"{hospital_name.lower().replace(' ', '')}_{index}@neurobridge.com"
                
                hospital = Hospital(
                    name=hospital_name,
                    email=email,
                    password=hospital_name,
                    city=str(row.get('city', 'Unknown')).strip()
                )
                db.session.add(hospital)
                db.session.commit()
                hospitals_created += 1
                if index < 5:  # Print first few for verification
                    print(f'Created hospital: {hospital.name} (ID: {hospital.id})')
            
            # Add donor or recipient
            data_type = str(row.get('type', '')).lower().strip()
            
            if data_type == 'donor':
                donor = Donor(
                    name=str(row['name']).strip(),
                    age=int(row['age']) if pd.notna(row['age']) else None,
                    blood_group=str(row['blood_group']).strip(),
                    organ=str(row['organ']).strip(),
                    city=str(row.get('city', '')).strip(),
                    phone=str(row.get('phone', '')).strip(),
                    hospital_id=hospital.id
                )
                db.session.add(donor)
                donors_added += 1
                if index < 5:
                    print(f'  Added donor: {donor.name} to {hospital.name}')
                    
            elif data_type == 'recipient':
                recipient = Recipient(
                    name=str(row['name']).strip(),
                    age=int(row['age']) if pd.notna(row['age']) else None,
                    blood_group=str(row['blood_group']).strip(),
                    organ=str(row['organ']).strip(),
                    urgency=str(row.get('urgency', 'Medium')).strip(),
                    city=str(row.get('city', '')).strip(),
                    phone=str(row.get('phone', '')).strip(),
                    hospital_id=hospital.id
                )
                db.session.add(recipient)
                recipients_added += 1
                if index < 5:
                    print(f'  Added recipient: {recipient.name} to {hospital.name}')
            else:
                errors.append(f"Row {index+1}: Invalid type '{data_type}'. Must be 'donor' or 'recipient'")
                
        except KeyError as e:
            errors.append(f"Row {index+1}: Missing required column {e}")
        except Exception as e:
            errors.append(f"Row {index+1}: Error - {str(e)[:100]}")
            db.session.rollback()
            continue
    
    # Final commit
    try:
        db.session.commit()
        print()
        print(f'✅ Upload completed successfully!')
        print(f'   Hospitals created: {hospitals_created}')
        print(f'   Donors added: {donors_added}')
        print(f'   Recipients added: {recipients_added}')
        
        # Verify final counts
        final_hospitals = len(Hospital.query.all())
        final_donors = len(Donor.query.all())
        final_recipients = len(Recipient.query.all())
        print()
        print(f'Database final state: {final_hospitals} hospitals, {final_donors} donors, {final_recipients} recipients')
        print(f'Growth: +{final_hospitals - initial_hospitals} hospitals, +{final_donors - initial_donors} donors, +{final_recipients - initial_recipients} recipients')
        
        if errors:
            print()
            print(f'⚠️  {len(errors)} errors encountered:')
            for err in errors[:5]:
                print(f'   - {err}')
            if len(errors) > 5:
                print(f'   ... and {len(errors) - 5} more')
    except Exception as e:
        db.session.rollback()
        print(f'❌ Database commit error: {e}')
