from app import app, db, Hospital, Donor, Recipient
import pandas as pd

with app.app_context():
    # Clean up test data first
    Hospital.query.filter_by(name='City Hospital').delete()
    Hospital.query.filter_by(name='Central Hospital').delete()
    db.session.commit()
    
    # Read and process test file
    df = pd.read_excel('test_upload.xlsx')
    print(f'Excel has {len(df)} rows')
    print('Columns:', list(df.columns))
    print()
    
    for idx, row in df.iterrows():
        print(f'Row {idx}: hospital={row["hospital"]}, type={row["type"]}, name={row["name"]}')
        
        hospital_name = str(row['hospital']).strip()
        hospital = Hospital.query.filter_by(name=hospital_name).first()
        
        if not hospital:
            hospital = Hospital(
                name=hospital_name,
                email=f'{hospital_name.lower().replace(" ", "")}@neurobridge.com',
                password=hospital_name,
                city=str(row.get('city', 'Unknown')).strip()
            )
            db.session.add(hospital)
            db.session.commit()
            print(f'  -> Created hospital: {hospital.name} (ID: {hospital.id})')
        else:
            print(f'  -> Hospital exists: {hospital.name} (ID: {hospital.id})')
        
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
            print(f'  -> Added donor: {donor.name}')
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
            print(f'  -> Added recipient: {recipient.name}')
    
    db.session.commit()
    print()
    print('Data saved successfully!')
    
    # Verify
    hospitals = Hospital.query.all()
    donors = Donor.query.all()
    recipients = Recipient.query.all()
    print(f'Database now has: {len(hospitals)} hospitals, {len(donors)} donors, {len(recipients)} recipients')
